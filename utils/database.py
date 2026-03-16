import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'leads.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            endereco TEXT,
            segmento TEXT,
            fonte TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_lead(nome, telefone, endereco='', segmento='Unhas', fonte='Google Maps'):
    conn = get_connection()
    conn.execute(
        'INSERT INTO leads (nome, telefone, endereco, segmento, fonte) VALUES (?, ?, ?, ?, ?)',
        (nome, telefone, endereco, segmento, fonte)
    )
    conn.commit()
    conn.close()

def get_all_leads():
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM leads ORDER BY data_coleta DESC')
    leads = cursor.fetchall()
    conn.close()
    return leads

def get_leads_count():
    conn = get_connection()
    cursor = conn.execute('SELECT COUNT(*) FROM leads')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def export_to_csv(filepath):
    import csv
    leads = get_all_leads()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Nome', 'Telefone', 'Endereco', 'Segmento', 'Fonte', 'Data'])
        for lead in leads:
            writer.writerow([lead['id'], lead['nome'], lead['telefone'], lead['endereco'], lead['segmento'], lead['fonte'], lead['data_coleta']])
    return len(leads)
