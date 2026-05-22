import json
import subprocess
from time import time
from bluezero import peripheral, adapter

from core.config import (
    SERVICE_UUID,
    AUTH_CHAR_UUID,
    CONFIG_CHAR_UUID,
    STATUS_CHAR_UUID,
    DEVICE_NAME,
    PROVISIONING_PIN,
    SESSION_TTL_SECONDS,
)
from core.crypto import (
    create_server_session,
    verify_client_proof,
    decrypt_credentials,
)
from core.protocol import parse_credentials
from core.wifi import connect_wifi


class ProvisioningServer:
    def __init__(self):
        self.status_message = "Servidor iniciado"
        self.last_auth_response = b'{"type":"not_ready"}'

        self.pending_session = None
        self.active_session = None
        self.closed_session_ids = set()

        self._prepare_bluetooth()

        adapters = list(adapter.list_adapters())
        if not adapters:
            raise RuntimeError("Nenhum adaptador Bluetooth encontrado")

        self.address = adapters[0]
        print(f"[BLE] Adaptador: {self.address}")

        self.app = peripheral.Peripheral(
            adapter_address=self.address,
            local_name=DEVICE_NAME,
        )

    def _set_status(self, message: str):
        self.status_message = message
        print(f"[STATUS] {message}")

    def _run(self, command):
        print(f"[CMD] {command}")
        subprocess.run(command, shell=True, check=False)

    def _prepare_bluetooth(self):
        print("[BLE] A preparar Bluetooth...")

        self._run("rfkill unblock bluetooth")
        self._run("bluetoothctl power on")
        self._run("bluetoothctl agent NoInputNoOutput")
        self._run("bluetoothctl default-agent")
        self._run("bluetoothctl discoverable on")
        self._run("bluetoothctl pairable on")
        self._run("bluetoothctl discoverable-timeout 0")

    def start(self):
        print("[BLE] A criar serviço GATT...")

        self.app.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

        self.app.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=AUTH_CHAR_UUID,
            value=[],
            notifying=False,
            flags=["read", "write"],
            read_callback=self.on_auth_read,
            write_callback=self.on_auth_write,
            notify_callback=None,
        )

        self.app.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=CONFIG_CHAR_UUID,
            value=[],
            notifying=False,
            flags=["write"],
            read_callback=None,
            write_callback=self.on_config_write,
            notify_callback=None,
        )

        self.app.add_characteristic(
            srv_id=1,
            chr_id=3,
            uuid=STATUS_CHAR_UUID,
            value=list(self.status_message.encode("utf-8")),
            notifying=True,
            flags=["read", "notify"],
            read_callback=self.on_status_read,
            write_callback=None,
            notify_callback=None,
        )

        print("--------------------------------------")
        print("[BLE] Servidor BLE ativo")
        print(f"[BLE] Nome: {DEVICE_NAME}")
        print(f"[BLE] Service: {SERVICE_UUID}")
        print(f"[BLE] Auth: {AUTH_CHAR_UUID}")
        print(f"[BLE] Config: {CONFIG_CHAR_UUID}")
        print(f"[BLE] Status: {STATUS_CHAR_UUID}")
        print("--------------------------------------")

        self.app.publish()

    def _json_response(self, payload: dict):
        self.last_auth_response = json.dumps(payload).encode("utf-8")

    def _session_expired(self, session) -> bool:
        return session is None or (time() - session.created_at) > SESSION_TTL_SECONDS

    def on_auth_write(self, value, options):
        raw = bytes(value).decode("utf-8", errors="replace")
        print(f"[AUTH] RAW: {raw}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._set_status("AUTH JSON invalido")
            self._json_response({"type": "error", "message": "json_invalido"})
            return

        msg_type = payload.get("type")

        try:
            if msg_type == "client_hello":
                # Uma sessão de provisionamento de cada vez.
                if self.active_session and not self.active_session.closed:
                    raise ValueError("ja existe uma sessao ativa")

                session, server_hello = create_server_session(payload, PROVISIONING_PIN)

                if session.session_id in self.closed_session_ids:
                    raise ValueError("session_id repetido")

                self.pending_session = session
                self._json_response(server_hello)
                self._set_status("server_hello pronto")
                return

            if msg_type == "client_proof":
                session = self.pending_session

                if self._session_expired(session):
                    self.pending_session = None
                    raise ValueError("sessao expirada")

                session_id = payload.get("session_id")
                if session_id != session.session_id:
                    raise ValueError("session_id invalido no client_proof")

                client_proof = payload.get("client_proof")
                if not verify_client_proof(session, client_proof):
                    raise ValueError("client_proof invalido")

                session.client_proof_ok = True
                self.active_session = session
                self.pending_session = None
                self._json_response({"type": "auth_ok", "session_id": session.session_id})
                self._set_status("sessao segura estabelecida")
                return

            raise ValueError(f"tipo AUTH desconhecido: {msg_type}")

        except Exception as exc:
            self._json_response({"type": "error", "message": str(exc)})
            self._set_status(f"AUTH erro: {exc}")

    def on_auth_read(self):
        print("[AUTH] READ")
        return list(self.last_auth_response)

    def on_config_write(self, value, options):
        raw = bytes(value).decode("utf-8", errors="replace")
        print(f"[CONFIG] RAW: {raw}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._set_status("CONFIG JSON invalido")
            return

        try:
            session = self.active_session

            if self._session_expired(session):
                self.active_session = None
                raise ValueError("sessao expirada")

            if not session.client_proof_ok:
                raise ValueError("client_proof ainda nao validado")

            if session.session_id in self.closed_session_ids:
                raise ValueError("session_id antigo/reutilizado")

            nonce = payload.get("nonce")
            if not nonce:
                raise ValueError("nonce em falta")

            if nonce in session.used_message_nonces:
                raise ValueError("nonce repetido")

            credentials = decrypt_credentials(session, payload)
            ssid, password = parse_credentials(credentials)

            # Marca o nonce como usado só depois de autenticar e validar o payload.
            session.used_message_nonces.add(nonce)

            ok = connect_wifi(ssid, password)

            session.closed = True
            self.closed_session_ids.add(session.session_id)
            self.active_session = None

            if ok:
                self._set_status(f"Wi-Fi configurado: {ssid}")
            else:
                self._set_status("Falha ao configurar Wi-Fi")

        except Exception as exc:
            self._set_status(f"CONFIG erro: {exc}")

    def on_status_read(self):
        print("[STATUS] READ")
        return list(self.status_message.encode("utf-8"))
