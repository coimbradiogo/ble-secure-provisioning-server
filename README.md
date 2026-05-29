# Secure BLE Provisioning for IoT Devices

Sistema de provisionamento seguro de credenciais Wi-Fi para dispositivos IoT através de Bluetooth Low Energy (BLE).

Este projeto foi desenvolvido no âmbito académico da ESTG com o objetivo de demonstrar um mecanismo seguro de configuração Wi-Fi para dispositivos IoT utilizando Bluetooth 4.1 e criptografia aplicada ao nível da aplicação.

---

# Objetivo

Dispositivos IoT normalmente necessitam de receber:

* SSID da rede Wi-Fi
* Password
* Configurações iniciais

No entanto, o Bluetooth 4.1 apresenta vulnerabilidades conhecidas:

* Eavesdropping
* Replay attacks
* MITM (Man-In-The-Middle)

Este projeto implementa uma camada de segurança adicional para garantir:

* Confidencialidade
* Integridade
* Autenticidade
* Proteção contra replay

---

# Tecnologias Utilizadas

## Mobile App

* Flutter
* flutter_blue_plus
* Dart

## Servidor IoT

* Python
* BlueZ / Bluezero
* Raspberry Pi / Linux
* D-Bus
* NetworkManager (`nmcli`)

## Segurança

* ECDH P-256
* AES-GCM 128-bit
* HKDF
* Nonces
* Session IDs

---

# Arquitetura

```text
App
     │
     │ BLE 4.1 + AES-GCM
     ▼
Raspberry Pi BLE Server
     │
     │ nmcli
     ▼
Wi-Fi Router
```

---

# Fluxo Seguro Implementado

## 1. Descoberta BLE

A aplicação Flutter procura dispositivos BLE disponíveis.

O Raspberry Pi anuncia:

* Nome BLE
* Serviço GATT
* Characteristics AUTH / CONFIG / STATUS

---

## 2. Handshake Seguro

A app envia:

```json
{
  "type": "client_hello"
}
```

O servidor:

* gera chaves ECDH temporárias
* cria um nonce único
* cria session_id
* deriva chave AES-GCM via HKDF

---

## 3. Autenticação

A aplicação envia:

* PIN de provisionamento
* prova criptográfica (`client_proof`)

O servidor valida:

* PIN
* assinatura
* integridade da sessão

---

## 4. Envio Seguro de Credenciais

A aplicação cifra:

```json
{
  "ssid": "MinhaRede",
  "password": "12345678"
}
```

usando:

* AES-GCM
* nonce único

e envia via characteristic CONFIG.

---

## 5. Configuração Wi-Fi

O servidor:

* decifra as credenciais
* valida a integridade
* configura Wi-Fi via `nmcli`

---

# Medidas de Segurança

## AES-GCM

Garante:

* confidencialidade
* autenticação
* integridade

As credenciais nunca circulam em texto limpo.

---

## ECDH P-256

Permite:

* derivação segura de chave
* Perfect Forward Secrecy

Cada sessão usa chaves temporárias diferentes.

---

## Nonces

Cada mensagem utiliza um nonce único para:

* impedir replay attacks
* impedir reutilização de mensagens capturadas

---

## Session IDs

Cada sessão BLE possui:

* identificador único
* validade temporária

Sessões antigas são rejeitadas.

---

# Estrutura do Projeto

```text
iot_server/
│
├── core/
│   ├── __init__.py
│   ├── ble_server.py
│   ├── config.py
│   ├── crypto.py
│   ├── protocol.py
│   └── wifi.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── main.py
```

---

# Instalação

## 1. Clonar repositório

```bash
git clone <repo>
cd iot_server
```

---

## 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Executar Servidor

```bash
sudo venv/bin/python main.py
```

---

# Configuração

Verificar em:

```text
core/config.py
```

* UUIDs BLE
* PIN de provisionamento
* configurações de segurança

Verificar interface Wi-Fi em:

```text
core/wifi.py
```

por defeito:

```python
wlo1
```

---

# Screenshots

## Aplicação Flutter

* descoberta BLE
* envio seguro de credenciais
* autenticação via PIN

## Servidor Raspberry Pi

* handshake seguro
* geração de sessão
* configuração Wi-Fi

---

# Estado Atual

✔ Descoberta BLE
✔ Handshake seguro
✔ AES-GCM funcional
✔ ECDH funcional
✔ Nonces e Session IDs
✔ Configuração Wi-Fi automática
✔ Flutter ↔ Raspberry Pi funcional

---

# Autor

Diogo Coimbra
Gabriel Santos
ESTG — Engenharia Informática
