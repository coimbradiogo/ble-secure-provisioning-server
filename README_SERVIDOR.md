# Servidor BLE de Provisionamento Seguro

Este servidor está alinhado com a app Flutter enviada.

## Fluxo implementado

1. A app escreve `client_hello` na characteristic AUTH.
2. O servidor gera ECDH P-256, `server_nonce`, `session_id`, deriva a chave AES-GCM por HKDF e devolve `server_hello` no READ da AUTH.
3. A app valida `server_proof`.
4. A app escreve `client_proof`.
5. O servidor valida `client_proof` e só depois aceita credenciais.
6. A app escreve `wifi_credentials` cifradas na CONFIG.
7. O servidor rejeita sessões antigas, nonces repetidos e timestamps fora da janela.
8. O servidor decifra AES-GCM e tenta configurar o Wi-Fi via `nmcli`.

## Executar

```bash
pip install -r requirements.txt
sudo python3 main.py
```

Confirma em `core/config.py`:
- `PROVISIONING_PIN`
- UUIDs
- interface Wi-Fi em `core/wifi.py`, por defeito `wlo1`
