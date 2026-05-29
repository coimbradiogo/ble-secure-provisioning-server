from time import time

from core.config import MAX_CLOCK_SKEW_SECONDS


def parse_credentials(credentials: dict) -> tuple[str, str]:
    ssid = credentials.get("ssid")
    password = credentials.get("password")

    if not ssid or not password:
        raise ValueError("SSID e password sao obrigatorios")

    timestamp_ms = credentials.get("timestamp")
    if not isinstance(timestamp_ms, int):
        raise ValueError("timestamp em falta ou invalido")

    now_ms = int(time() * 1000)
    max_skew_ms = MAX_CLOCK_SKEW_SECONDS * 1000

    if abs(now_ms - timestamp_ms) > max_skew_ms:
        raise ValueError("timestamp fora da janela permitida")

    return ssid, password
