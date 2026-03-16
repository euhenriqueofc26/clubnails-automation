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
            instagram TEXT,
            site TEXT,
            nota REAL,
            segmento TEXT,
            fonte TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_lead(nome, telefone='', endereco='', segmento='Unhas', fonte='Google Maps', instagram='', site='', nota=None):
    conn = get_connection()
    conn.execute(
        '''INSERT INTO leads (nome, telefone, endereco, instagram, site, nota, segmento, fonte) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (nome, telefone, endereco, instagram, site, nota, segmento, fonte)
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
        writer.writerow(['ID', 'Nome', 'Telefone', 'WhatsApp', 'Endereco', 'Instagram', 'Site', 'Nota', 'Segmento', 'Fonte', 'Data_Coleta'])
        for lead in leads:
            writer.writerow([
                lead['id'],
                lead['nome'],
                lead['telefone'],
                'https://wa.me/' + lead['telefone'].replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '') if lead['telefone'] else '',
                lead['endereco'],
                lead['instagram'],
                lead['site'],
                lead['nota'],
                lead['segmento'],
                lead['fonte'],
                lead['data_coleta']
            ])
    return len(leads)

def search_leads(query):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM leads WHERE nome LIKE ? OR telefone LIKE ? OR segmento LIKE ?",
        (f'%{query}%', f'%{query}%', f'%{query}%')
    )
    leads = cursor.fetchall()
    conn.close()
    return leads
