from core.crypto import encrypt

def receive_data():
    print("Simulação de envio seguro...")

    ssid = input("SSID: ")
    password = input("Password: ")

    data = {
        "ssid": ssid,
        "password": password
    }

    encrypted = encrypt(data)

    print("Payload enviado:", encrypted)

    return encrypted
    
if __name__ == "__main__":
    receive_data()
