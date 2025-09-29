from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = 'patio.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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
        cor_map = {"Verde": "#28a745", "Vermelho": "#dc3545", "Amarelo": "#ffc107"}
        vaga_dict['cor'] = cor_map.get(vaga['status_led'])
        vagas_list.append(vaga_dict)
        
    return jsonify(vagas_list)

if __name__ == '__main__':
    app.run(debug=True, port=5001)