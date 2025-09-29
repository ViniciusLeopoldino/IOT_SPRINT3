import sqlite3

DB_FILE = 'patio.db'
print(f"Resetando o banco de dados '{DB_FILE}'...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Apaga a tabela antiga se ela existir, para garantir um início limpo
cursor.execute("DROP TABLE IF EXISTS vagas")

# Cria a tabela novamente com a estrutura correta
cursor.execute('''
    CREATE TABLE vagas (
        id_vaga TEXT PRIMARY KEY,
        status TEXT CHECK(status IN ('Vazia', 'Ocupada', 'Manutencao')),
        placa_moto TEXT,
        status_led TEXT,
        ultimo_update TEXT
    );
''')

# Pré-cadastra as vagas no sistema com um estado inicial conhecido
# A VAGA 'B-01' EM MANUTENÇÃO FOI REMOVIDA DAQUI
vagas_iniciais = [('A-01', 'Vazia', None, 'Verde'),
                  ('A-02', 'Vazia', None, 'Verde'),
                  ('A-03', 'Vazia', None, 'Verde')]

cursor.executemany('''
    INSERT INTO vagas (id_vaga, status, placa_moto, status_led)
    VALUES (?, ?, ?, ?);
''', vagas_iniciais)


conn.commit()
conn.close()
print("Banco de dados resetado com sucesso. Agora com 3 vagas operacionais.")