# Mottu Storage IoT - Sistema de Gerenciamento de Pátio

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask-green.svg)
![Protocol](https://img.shields.io/badge/Protocol-MQTT-red.svg)
![Database](https://img.shields.io/badge/Database-SQLite-blue.svg)

Este projeto é um protótipo funcional de um sistema de gerenciamento de pátio para a **Mottu**, utilizando uma arquitetura baseada em **Internet das Coisas (IoT)**. A solução simula o monitoramento em tempo real de vagas de estacionamento através de dispositivos IoT, oferecendo uma visão centralizada e controle para os gestores do armazém.

---

## 🎯 Problema de Negócio

A gestão de grandes pátios de motocicletas é um desafio logístico. O controle manual sobre a ocupação das vagas é lento, suscetível a erros humanos e não fornece uma visão instantânea do status do pátio. Isso dificulta a localização de veículos, otimização do espaço e a operação diária.

## 💡 Solução Proposta

Implementamos uma solução de IoT onde cada vaga de estacionamento é equipada com um dispositivo "inteligente" (simulado). Este dispositivo monitora o status da vaga (Vazia, Ocupada, Manutenção) e identifica a moto estacionada.

Os dados são transmitidos em tempo real via protocolo **MQTT** para um sistema central que os persiste em um banco de dados e os exibe em duas interfaces web distintas:
1.  **Dashboard de Visualização:** Um painel "read-only" para monitoramento geral, ideal para ser exibido em telas no pátio.
2.  **Painel de Gestão:** Uma interface de controle completa para os gestores do armazém, permitindo iniciar/parar a simulação de vagas e registrar a entrada e saída de veículos.

---

## 🏛️ Arquitetura do Sistema

O projeto é desacoplado e modular, composto pelos seguintes serviços independentes:

1.  **`vaga_iot_simulator.py` (Dispositivo IoT Simulado):**
    * Um script Python que representa o hardware de uma vaga.
    * Cada instância é um processo independente que se conecta ao Broker MQTT.
    * É iniciado e parado remotamente pelo Painel de Gestão.
    * Sua principal função é estar "online" para que o sistema saiba que a vaga está ativa.

2.  **Broker MQTT (Nuvem):**
    * Utilizamos um broker público (`broker.hivemq.com`) como o sistema central de mensagens, responsável pela comunicação em tempo real entre todos os componentes.

3.  **`mqtt_listener.py` (Serviço Coletor):**
    * Um serviço de backend que fica rodando continuamente.
    * Ele se inscreve no tópico MQTT geral e "ouve" todas as mensagens de telemetria enviadas pelas vagas.
    * É o único serviço responsável por processar os dados e escrevê-los no banco de dados SQLite.

4.  **`dashboard_app.py` (Aplicação do Dashboard Visual):**
    * Um servidor web Flask (rodando na porta `5001`) que serve uma página de visualização.
    * A página busca os dados mais recentes do banco de dados via uma API interna e exibe o status de cada vaga, atualizando-se periodicamente. Não possui controles.

5.  **`manager_app.py` (Aplicação do Painel de Gestão):**
    * Um segundo servidor web Flask (rodando na porta `5002`) que serve a interface de controle.
    * Permite ao gestor:
        * Iniciar e parar os processos dos simuladores de vagas.
        * Simular o estacionamento de uma moto (enviando um comando MQTT).
        * Simular a saída de uma moto (enviando outro comando MQTT).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Backend:** Flask
* **Comunicação IoT:** Paho MQTT
* **Banco de Dados:** SQLite 3
* **Interface:** HTML, CSS, JavaScript (com Fetch API)

---

## 📂 Estrutura de Arquivos

```
.
├── dashboard_app.py      # Servidor Flask para o painel visual
├── manager_app.py        # Servidor Flask para o painel do gestor
├── mqtt_listener.py      # Serviço que ouve o MQTT e salva no DB
├── database.py           # Script para criar/resetar o banco de dados
├── vaga_iot_simulator.py # Script que simula o dispositivo IoT da vaga
├── requirements.txt      # Dependências do projeto
└── templates/
    ├── dashboard.html    # HTML do painel visual
    └── manager.html      # HTML do painel do gestor
```

---

## ▶️ Como Executar o Sistema

Para rodar o projeto, você precisará de **3 terminais**.

### 1. Pré-requisitos
* Python 3.8+
* `pip` (gerenciador de pacotes)

### 2. Instalação
```bash
# Clone o repositório
git clone https://github.com/ViniciusLeopoldino/IOT_SPRINT3.git
cd IOT_SPRINT3

# Crie e ative um ambiente virtual (recomendado)
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Inicialização do Banco de Dados
Este passo só precisa ser executado uma vez (ou sempre que quiser resetar o pátio).

```bash
python database.py
```

### 4. Execução dos Serviços
Inicie cada serviço em seu próprio terminal, na ordem abaixo:

* **Terminal 1 - Listener MQTT:**
    ```bash
    python mqtt_listener.py
    ```

* **Terminal 2 - Dashboard Visual:**
    ```bash
    python dashboard_app.py
    ```

* **Terminal 3 - Painel do Gestor:**
    ```bash
    python manager_app.py
    ```

### 5. Utilização
1.  **Abra o Dashboard Visual** no navegador: `http://127.0.0.1:5001`
2.  **Abra o Painel do Gestor** em outra aba: `http://127.0.0.1:5002`
3.  Use o **Painel do Gestor** para controlar toda a simulação:
    * Clique em "Iniciar" para "ligar" os sensores das vagas.
    * Preencha uma placa e clique em "Estacionar" para simular a chegada de uma moto.
    * Observe que o status muda tanto no painel do gestor quanto no dashboard visual.

---

## 👨‍💻 Integrantes

* **RM:** 557047 **Nome:** Vinicius Leopoldino de Oliveira
* **RM:** 556834 **Nome:** Pablo Lopes Doria de Andrade
* **Curso:** Análise e Desenvolvimento de Sistemas - FIAP
* **Matéria:** Disruptive Architectures: IoT, IOB & Generative IA
