from time import time

from core.config import MAX_CLOCK_SKEW_SECONDS, PROVISIONING_PIN


def validate_timestamp(timestamp_ms: int):
    if not isinstance(timestamp_ms, int):
        raise ValueError("timestamp em falta ou invalido")

    now_ms = int(time() * 1000)
    max_skew_ms = MAX_CLOCK_SKEW_SECONDS * 1000

    if abs(now_ms - timestamp_ms) > max_skew_ms:
        raise ValueError("timestamp fora da janela permitida")


def parse_credentials(credentials: dict, timestamp_ms: int) -> tuple[str, str]:
    validate_timestamp(timestamp_ms)

    ssid = credentials.get("ssid")
    password = credentials.get("password")
    provisioning_pin = credentials.get("provisioning_pin")

    if not ssid or not password:
        raise ValueError("SSID e password sao obrigatorios")

    if provisioning_pin != PROVISIONING_PIN:
        raise ValueError("PIN de provisionamento invalido")

    return ssid, password
