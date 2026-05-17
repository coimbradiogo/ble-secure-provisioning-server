from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import json
import base64

# chave fixa (para já)
KEY = b'1234567890123456'  # 16 bytes (AES-128)

def encrypt(data_dict):
    aesgcm = AESGCM(KEY)

    nonce = os.urandom(12)

    data = json.dumps(data_dict).encode()

    ciphertext = aesgcm.encrypt(nonce, data, None)

    return {
        "ciphertext": ciphertext.hex(),
        "nonce": nonce.hex()
    }


def decrypt(payload):
    try:
        aesgcm = AESGCM(KEY)

        

        nonce = base64.b64decode(payload["nonce"])
        ciphertext = base64.b64decode(payload["ciphertext"])

        decrypted = aesgcm.decrypt(nonce, ciphertext, None)

        data = json.loads(decrypted.decode())

        return data

    except Exception as e:
        print("Erro na desencriptação:", e)
        return None
