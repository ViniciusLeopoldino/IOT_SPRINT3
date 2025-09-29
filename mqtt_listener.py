import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime

DB_FILE = 'patio.db'
BROKER = 'broker.hivemq.com'
PORT = 1883
TOPIC = "mottu/patio/vaga/+/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Listener MQTT conectado e ouvindo o tópico de telemetria.")
        client.subscribe(TOPIC)
    else:
        print(f"Falha na conexão do Listener, código: {rc}")

def on_message(client, userdata, msg):
    try:
        id_vaga = msg.topic.split('/')[3]
        payload = json.loads(msg.payload.decode())
        status = payload.get('status')
        placa = payload.get('placa_moto')
        timestamp = datetime.now().isoformat()

        print(f"Dados recebidos da vaga {id_vaga}: {payload}")

        led_status_map = {"Vazia": "Verde", "Ocupada": "Vermelho", "Manutencao": "Amarelo"}
        led_status = led_status_map.get(status, "Vermelho")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vagas SET status = ?, placa_moto = ?, status_led = ?, ultimo_update = ? WHERE id_vaga = ?
        ''', (status, placa, led_status, timestamp, id_vaga))
        conn.commit()
        conn.close()
        print(f"Banco de dados atualizado para a vaga {id_vaga}.")
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)

client.loop_forever()