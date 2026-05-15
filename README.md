# Secure BLE Provisioning Server (IoT)

Este repositório contém a componente de servidor para o projeto de **Provisionamento Seguro de Credenciais via BLE** desenvolvido na ESTG.

O sistema foi desenhado para configurar redes Wi-Fi em dispositivos IoT de forma segura, mesmo utilizando a norma **Bluetooth 4.1**, através de uma camada adicional de cifragem na aplicação.

## 🛡️ Arquitetura de Segurança

Para mitigar as vulnerabilidades nativas do Bluetooth 4.1 (como Eavesdropping e MITM), implementámos as seguintes defesas:

* **Cifragem End-to-End:** Uso de **AES-GCM (128-bit)** para garantir que as credenciais nunca viajam em texto limpo.
* **Integridade Garantida:** Tags de autenticação que impedem a modificação dos dados por terceiros.
* **Proteção contra Replay:** Implementação de **Nonces** únicos por sessão, impedindo que comandos capturados sejam reutilizados.
* **Pairing Seguro:** Configuração de agentes `DisplayOnly` para garantir prova de posse física via PIN.

## 📂 Estrutura de Ficheiros

* `main.py`: Orquestrador principal do serviço.
* `core/ble_server.py`: Implementação do Servidor GATT e Periférico.
* `core/crypto.py`: Módulo crítico de criptografia (AES-GCM).
* `core/wifi.py`: Automação da ligação Wi-Fi via `nmcli`.
* `core/server.py`: Simulador da aplicação móvel para testes de cifragem. (eliminado por não ter muita relevância)

## 🚀 Como Executar

1. **Instalar dependências:**
   ```bash
   pip install cryptography dbus-python
