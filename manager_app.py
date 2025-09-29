from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import paho.mqtt.client as mqtt
import json
import subprocess
import sys

app = Flask(__name__)
DB_FILE = 'patio.db'
BROKER = 'broker.hivemq.com'
PORT = 1883

# --- CLIENTE MQTT PERSISTENTE PARA O GESTOR ---
# Este cliente será usado para ENVIAR todos os comandos do painel.
# Ele mantém uma conexão estável com o broker.
mqtt_publisher = mqtt.Client()
mqtt_publisher.connect(BROKER, PORT, 60)
# Inicia o loop em uma thread para manter a conexão viva e lidar com reconexões.
mqtt_publisher.loop_start()


# Dicionário em memória para rastrear os processos dos simuladores
simuladores_processos = {}

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def manager():
    return render_template('manager.html')

@app.route('/api/status_vagas')
def api_status_vagas():
    conn = get_db_connection()
    vagas_db = conn.execute('SELECT * FROM vagas ORDER BY id_vaga').fetchall()
    conn.close()
    
    vagas_list = []
    for vaga in vagas_db:
        vaga_dict = dict(vaga)
        process = simuladores_processos.get(vaga['id_vaga'])
        vaga_dict['simulador_ativo'] = process is not None and process.poll() is None
        vagas_list.append(vaga_dict)
        
    return jsonify(vagas_list)

@app.route('/comando', methods=['POST'])
def comando():
    id_vaga = request.form['id_vaga']
    action = request.form['action']

    if action == 'start':
        process = simuladores_processos.get(id_vaga)
        if process is None or process.poll() is not None:
            cmd = [sys.executable, 'vaga_iot_simulator.py', '--vaga', id_vaga]
            process = subprocess.Popen(cmd)
            simuladores_processos[id_vaga] = process
            print(f"Processo do simulador da vaga {id_vaga} iniciado (PID: {process.pid}).")

    elif action == 'stop':
        process = simuladores_processos.get(id_vaga)
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait()
            print(f"Processo do simulador da vaga {id_vaga} terminado.")
            del simuladores_processos[id_vaga]

    else: # Ações de 'estacionar' e 'sair'
        topic = f"mottu/patio/vaga/{id_vaga}/telemetry"
        payload = {}
        if action == 'estacionar':
            placa = request.form['placa']
            payload = {"status": "Ocupada", "placa_moto": placa.upper()}
        elif action == 'sair':
            payload = {"status": "Vazia", "placa_moto": None}
        
        if payload:
            # --- CORREÇÃO PRINCIPAL AQUI ---
            # Usamos nosso cliente MQTT global e persistente para publicar.
            # Isso é rápido e confiável.
            mqtt_publisher.publish(topic, json.dumps(payload))
            print(f"Comando '{action}' para a vaga {id_vaga} enviado via MQTT com sucesso.")

    return redirect(url_for('manager'))


if __name__ == '__main__':
    app.run(debug=True, port=5002, use_reloader=False)