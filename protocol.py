from core.crypto import decrypt

def parse_credentials(payload):
    data = decrypt(payload)

    if not data:
        return None, None

    ssid = data.get("ssid")
    password = data.get("password")

    if not ssid or not password:
        print("Dados invÃ¡lidos")
        return None, None

    return ssid, password
