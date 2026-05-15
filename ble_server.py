import json
import os
from bluezero import peripheral, adapter
from core.protocol import parse_credentials
from core.wifi import connect_wifi

# UUIDs do Projeto 38
SERVICE_UUID = '12345678-1234-5678-1234-567812345678'
CHAR_UUID = '87654321-4321-8765-4321-876543210987'

class ProvisioningServer:
    def __init__(self):
        os.system(f"bluetoothctl power on")
        os.system(f"bluetoothctl discoverable on")
        os.system(f"bluetoothctl pairable on")
        os.system("bluetoothctl discoverable-timeout 0")
        # Passo crítico: Encontrar o endereço real do adaptador Bluetooth
        # Isso evita que o dbus receba 'None' e cause o TypeError
        all_adapters = list(adapter.list_adapters())
        if not all_adapters:
            raise Exception("Nenhum adaptador Bluetooth encontrado!")
        
        # Usa o primeiro adaptador disponível (ex: 'hci0')
        self.address = all_adapters[0]
        print(f"Usando adaptador: {self.address}")

        self.app = peripheral.Peripheral(adapter_address=self.address, 
                                         local_name='IoT_Provisioner')
        
    def on_write_request(self, value, options):
        try:
            payload_raw = bytes(value).decode('utf-8')
            payload = json.loads(payload_raw)
            print(f"Recebido via BLE: {payload}")

            ssid, password = parse_credentials(payload)

            if ssid and password:
                connect_wifi(ssid, password)
            else:
                print("Erro: Dados de credenciais inválidos.")
        except Exception as e:
            print(f"Erro no processamento BLE: {e}")

    def start(self):
        self.app.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)
        self.app.add_characteristic(srv_id=1, chr_id=1, uuid=CHAR_UUID,
                                    value=[], notifying=False,
                                    flags=['write'],
                                    read_callback=None,
                                    write_callback=self.on_write_request,
                                    notify_callback=None)
        
        print("--- Servidor BLE Projeto 38 Ativo ---")
        self.app.publish()
