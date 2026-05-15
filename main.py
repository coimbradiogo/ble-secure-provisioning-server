from core.ble_server import ProvisioningServer

def main():
    print("--- Sistema de Provisionamento IoT ---")
    
    # Inicia o servidor Bluetooth
    ble_provisioner = ProvisioningServer()
    
    try:
        ble_provisioner.start()
    except KeyboardInterrupt:
        print("\nServidor parado pelo utilizador.")

if __name__ == "__main__":
    main()
