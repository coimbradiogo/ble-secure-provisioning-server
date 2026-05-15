import os

def connect_wifi(ssid, password):
    print(f"A tentar ligar ao Wi-Fi: {ssid}...")
    
    # 1. Tenta apagar uma ligação antiga com o mesmo nome para evitar conflitos
    os.system(f'sudo nmcli connection delete "{ssid}" > /dev/null 2>&1')
    
    # 2. Cria a nova ligação com os parâmetros que funcionaram no teu terminal
    # Nota: Usamos 'ifname wlo1' porque é a tua interface real
    comando_add = (f'nmcli connection add type wifi con-name "{ssid}" ifname wlo1 ssid "{ssid}" -- '
                   f'wifi-sec.key-mgmt wpa-psk wifi-sec.psk "{password}"')
    
    print("A configurar perfil de rede...")
    os.system(comando_add)
    
    # 3. Ativa a ligação
    print("A ativar ligação...")
    resultado = os.system(f'nmcli connection up "{ssid}"')
    
    if resultado == 0:
        print(f"--- SUCESSO: Conectado à rede {ssid} ---")
        return True
    else:
        print("--- ERRO: Falha na ativação do Wi-Fi ---")
        return False
