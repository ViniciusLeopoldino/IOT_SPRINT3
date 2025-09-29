from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime

# --- CONFIGURAÇÃO GLOBAL ---
DB_FILE = 'patio.db'
BROKER = 'broker.hivemq.com'
PORT = 1883
app = Flask(__name__)

# --- GERENCIADOR DE SIMULADORES EM MEMÓRIA ---
simuladores_ativos = {}
lock = threading.Lock()

# --- CLIENTE MQTT ÚNICO E PERSISTENTE ---
# Criamos um cliente MQTT que será usado por toda a aplicação
mqtt_client = mqtt.Client()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- FUNÇÕES DE CALLBACK DO MQTT ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao Broker MQTT com sucesso!")
        # Se inscreve no tópico para receber dados das vagas
        client.subscribe("mottu/patio/vaga/+/telemetry")
    else:
        print(f"Falha na conexão com o MQTT, código: {rc}")

def on_message(client, userdata, msg):
    with lock:
        try:
            id_vaga = msg.topic.split('/')[3]
            payload = json.loads(msg.payload.decode())
            status = payload.get('status')
            placa = payload.get('placa_moto')
            timestamp = datetime.now().isoformat()

            print(f"Listener recebeu de {id_vaga}: {payload}")

            led_status_map = {"Vazia": "Verde", "Ocupada": "Vermelho", "Manutencao": "Amarelo"}
            led_status = led_status_map.get(status, "Vermelho")

            conn = get_db_connection()
            conn.execute('''
                UPDATE vagas SET status = ?, placa_moto = ?, status_led = ?, ultimo_update = ? WHERE id_vaga = ?
            ''', (status, placa, led_status, timestamp, id_vaga))
            conn.commit()
            conn.close()
            print(f"Banco de dados atualizado para a vaga {id_vaga}.")
        except Exception as e:
            print(f"Erro ao processar mensagem MQTT: {e}")

# --- ROTAS DA APLICAÇÃO WEB (FLASK) ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/vagas')
def api_vagas():
    conn = get_db_connection()
    vagas_db = conn.execute('SELECT * FROM vagas ORDER BY id_vaga').fetchall()
    conn.close()
    
    vagas_list = []
    for vaga in vagas_db:
        vaga_dict = dict(vaga)
        vaga_dict['simulador_ativo'] = simuladores_ativos.get(vaga['id_vaga'], False)
        cor_map = {"Verde": "#28a745", "Vermelho": "#dc3545", "Amarelo": "#ffc107"}
        vaga_dict['cor'] = cor_map.get(vaga['status_led'])
        vagas_list.append(vaga_dict)
        
    return jsonify(vagas_list)

@app.route('/comando', methods=['POST'])
def comando():
    id_vaga = request.form['id_vaga']
    action = request.form['action']
    
    if action == 'start_stop':
        simuladores_ativos[id_vaga] = not simuladores_ativos.get(id_vaga, False)
        status_sim = "iniciado" if simuladores_ativos[id_vaga] else "parado"
        print(f"Simulador da vaga {id_vaga} {status_sim}.")
    else:
        if not simuladores_ativos.get(id_vaga):
            return redirect(url_for('dashboard'))

        topic = f"mottu/patio/vaga/{id_vaga}/telemetry"
        payload = {}

        if action == 'estacionar':
            placa = request.form['placa']
            payload = {"status": "Ocupada", "placa_moto": placa.upper()}
        elif action == 'sair':
            payload = {"status": "Vazia", "placa_moto": None}

        if payload:
            # USA O CLIENTE GLOBAL E PERSISTENTE PARA PUBLICAR
            mqtt_client.publish(topic, json.dumps(payload))
            print(f"Comando '{action}' para a vaga {id_vaga} publicado com sucesso.")

    return redirect(url_for('dashboard'))

# --- INICIALIZAÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    # Atribui as funções de callback ao nosso cliente global
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    # Conecta ao broker
    mqtt_client.connect(BROKER, PORT, 60)
    
    # Inicia o loop do cliente MQTT em uma thread separada.
    # Isso é essencial: ele lida com o envio, recebimento e reconexões automaticamente.
    mqtt_client.loop_start()
    
    # Inicia a aplicação Flask
    app.run(debug=True, port=5001)