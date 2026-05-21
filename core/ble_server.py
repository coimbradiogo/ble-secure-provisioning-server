import json
import os
from bluezero import peripheral, adapter
from core.protocol import parse_credentials
from core.wifi import connect_wifi

SERVICE_UUID = '12345678-1234-5678-1234-567812345678'

AUTH_CHAR_UUID = '87654321-4321-8765-4321-876543210988'
CONFIG_CHAR_UUID = '87654321-4321-8765-4321-876543210987'
STATUS_CHAR_UUID = '87654321-4321-8765-4321-876543210989'


class ProvisioningServer:
    def __init__(self):
        os.system("bluetoothctl power on")
        os.system("bluetoothctl discoverable on")
        os.system("bluetoothctl pairable on")
        os.system("bluetoothctl discoverable-timeout 0")

        all_adapters = list(adapter.list_adapters())
        if not all_adapters:
            raise Exception("Nenhum adaptador Bluetooth encontrado!")

        self.address = all_adapters[0]
        print(f"Usando adaptador: {self.address}")

        self.app = peripheral.Peripheral(
            adapter_address=self.address,
            local_name='IoT_Provisioner'
        )

    def start(self):
        self.app.add_service(
            srv_id=1,
            uuid=SERVICE_UUID,
            primary=True
        )

        self.app.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=AUTH_CHAR_UUID,
            value=[],
            notifying=False,
            flags=['read', 'write'],
            read_callback=self.on_auth_read,
            write_callback=self.on_auth_write,
            notify_callback=None
        )

        self.app.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=CONFIG_CHAR_UUID,
            value=[],
            notifying=False,
            flags=['write'],
            read_callback=None,
            write_callback=self.on_config_write,
            notify_callback=None
        )

        self.app.add_characteristic(
            srv_id=1,
            chr_id=3,
            uuid=STATUS_CHAR_UUID,
            value=[],
            notifying=True,
            flags=['read', 'notify'],
            read_callback=self.on_status_read,
            write_callback=None,
            notify_callback=None
        )

        print("--- Servidor BLE Seguro Ativo ---")
        self.app.publish()

    def on_auth_write(self, value, options):
        print("AUTH recebeu:", bytes(value).decode("utf-8"))

    def on_auth_read(self):
        print("AUTH read pedido")
        return list(b'{"type":"server_hello_placeholder"}')

    def on_config_write(self, value, options):
        print("CONFIG recebeu:", bytes(value).decode("utf-8"))

    def on_status_read(self):
        return list(b"Servidor BLE ativo")