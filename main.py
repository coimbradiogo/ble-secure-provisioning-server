from core.ble_server import ProvisioningServer


def main():
    print("======================================")
    print(" Sistema de Provisionamento IoT Seguro")
    print("======================================")

    server = ProvisioningServer()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Parado pelo utilizador")


if __name__ == "__main__":
    main()
