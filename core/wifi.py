import os
import shlex


def connect_wifi(ssid, password, interface="wlo1"):
    print(f"A tentar ligar ao Wi-Fi: {ssid}...")

    safe_ssid = shlex.quote(ssid)
    safe_password = shlex.quote(password)
    safe_interface = shlex.quote(interface)

    os.system(f"sudo nmcli connection delete {safe_ssid} > /dev/null 2>&1")

    comando_add = (
        f"nmcli connection add type wifi con-name {safe_ssid} "
        f"ifname {safe_interface} ssid {safe_ssid} -- "
        f"wifi-sec.key-mgmt wpa-psk wifi-sec.psk {safe_password}"
    )

    print("A configurar perfil de rede...")
    add_result = os.system(comando_add)
    if add_result != 0:
        print("--- ERRO: Falha ao criar perfil Wi-Fi ---")
        return False

    print("A ativar ligação...")
    resultado = os.system(f"nmcli connection up {safe_ssid}")

    if resultado == 0:
        print(f"--- SUCESSO: Conectado à rede {ssid} ---")
        return True

    print("--- ERRO: Falha na ativação do Wi-Fi ---")
    return False
