import base64
import json
import os
import hmac
import hashlib
from dataclasses import dataclass, field
from time import time
from typing import Set

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from core.config import PROTOCOL_VERSION


@dataclass
class SecureSession:
    session_id: str
    key: bytes
    client_nonce: bytes
    server_nonce: bytes
    client_public_key: bytes
    server_public_key: bytes
    server_private_key: ec.EllipticCurvePrivateKey
    created_at: float = field(default_factory=time)
    client_proof_ok: bool = False
    used_message_nonces: Set[str] = field(default_factory=set)
    closed: bool = False


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def read_b64(payload: dict, field: str) -> bytes:
    value = payload.get(field)
    if not value:
        raise ValueError(f"{field} em falta")
    try:
        return base64.b64decode(value, validate=True)
    except Exception as exc:
        raise ValueError(f"{field} nao esta em base64 valido") from exc


def xor_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("nonces com tamanhos diferentes")
    return bytes(x ^ y for x, y in zip(a, b))


def public_key_bytes(private_key) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )


def load_client_public_key(public_key_raw: bytes):
    return ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(),
        public_key_raw,
    )


def create_server_session(client_hello: dict, provisioning_pin: str):
    if client_hello.get("version") != PROTOCOL_VERSION:
        raise ValueError("versao do protocolo invalida")

    client_nonce = read_b64(client_hello, "client_nonce")
    client_public_key = read_b64(client_hello, "client_public_key")

    if len(client_nonce) != 16:
        raise ValueError("client_nonce deve ter 16 bytes")

    server_private_key = ec.generate_private_key(ec.SECP256R1())
    server_public_key = public_key_bytes(server_private_key)

    peer_public_key = load_client_public_key(client_public_key)
    shared_secret = server_private_key.exchange(ec.ECDH(), peer_public_key)

    server_nonce = os.urandom(16)
    session_id = b64(os.urandom(12))

    salt = xor_bytes(client_nonce, server_nonce)
    info = f"ble-provisioning-v{PROTOCOL_VERSION}|{session_id}|{provisioning_pin}".encode()

    key = HKDF(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
        info=info,
    ).derive(shared_secret)

    session = SecureSession(
        session_id=session_id,
        key=key,
        client_nonce=client_nonce,
        server_nonce=server_nonce,
        client_public_key=client_public_key,
        server_public_key=server_public_key,
        server_private_key=server_private_key,
    )

    server_hello = {
        "type": "server_hello",
        "version": PROTOCOL_VERSION,
        "session_id": session_id,
        "server_nonce": b64(server_nonce),
        "server_public_key": b64(server_public_key),
        "server_proof": create_proof(session, "server"),
    }

    return session, server_hello


def create_proof(session: SecureSession, label: str) -> str:
    transcript = (
        f"ble-provisioning|{label}|{session.session_id}|".encode()
        + session.client_nonce
        + session.server_nonce
        + session.client_public_key
        + session.server_public_key
    )

    return b64(hmac.new(session.key, transcript, hashlib.sha256).digest())


def verify_client_proof(session: SecureSession, client_proof: str) -> bool:
    expected = create_proof(session, "client")
    return hmac.compare_digest(expected, client_proof or "")


def decrypt_credentials(session: SecureSession, payload: dict) -> dict:
    if payload.get("version") != PROTOCOL_VERSION:
        raise ValueError("versao do protocolo invalida")

    if payload.get("type") != "wifi_credentials":
        raise ValueError("tipo de mensagem invalido")

    if payload.get("session_id") != session.session_id:
        raise ValueError("session_id invalido")

    timestamp = payload.get("timestamp")
    if not isinstance(timestamp, int):
        raise ValueError("timestamp em falta ou invalido")

    nonce = read_b64(payload, "nonce")
    ciphertext = read_b64(payload, "ciphertext")

    if len(nonce) != 12:
        raise ValueError("nonce AES-GCM deve ter 12 bytes")

    aad = f"ble-provisioning-v{PROTOCOL_VERSION}|{session.session_id}|{timestamp}".encode()

    if payload.get("aad"):
        received_aad = read_b64(payload, "aad")
        if received_aad != aad:
            raise ValueError("AAD invalido")

    aesgcm = AESGCM(session.key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, aad)

    return json.loads(plaintext.decode("utf-8"))
