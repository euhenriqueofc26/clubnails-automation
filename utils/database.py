import sqlite3
import os
from utils.logger import log_info, log_erro

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'leads.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            maps_link TEXT UNIQUE,
            telefone TEXT,
            instagram TEXT,
            endereco TEXT,
            categoria TEXT,
            avaliacao REAL,
            fonte TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pendente'
        )
    ''')
    
    # Add instagram column if not exists
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN instagram TEXT")
    except:
        pass
    
    conn.commit()
    conn.close()
    log_info(f"Banco de dados inicializado: {DB_PATH}")

def link_existe(maps_link):
    if not maps_link:
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads WHERE maps_link = ?", (maps_link,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def salvar_lead(dados):
    if not dados.get('maps_link'):
        return False
    
    if link_existe(dados['maps_link']):
        log_info(f"Lead duplicado ignorado: {dados.get('nome', 'sem nome')}")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO leads (nome, maps_link, telefone, instagram, endereco, categoria, avaliacao, fonte, data_coleta, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'google_maps', datetime('now'), 'pendente')
        """, (
            dados.get('nome', ''),
            dados.get('maps_link', ''),
            dados.get('telefone', ''),
            dados.get('instagram', ''),
            dados.get('endereco', ''),
            dados.get('categoria', ''),
            dados.get('avaliacao', 0)
        ))
        conn.commit()
        if cursor.rowcount > 0:
            log_info(f"Novo lead salvo: {dados.get('nome', 'sem nome')}")
            return True
        return False
    except sqlite3.IntegrityError as e:
        log_info(f"Lead duplicado ignorado: {dados.get('nome', 'sem nome')}")
        return False
    except Exception as e:
        log_erro(f"Erro ao salvar lead: {e}")
        return False
    finally:
        conn.close()

def get_total_leads():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_leads_por_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as total FROM leads GROUP BY status")
    results = cursor.fetchall()
    conn.close()
    return {row['status']: row['total'] for row in results}

def get_all_maps_links():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maps_link FROM leads WHERE maps_link IS NOT NULL AND maps_link != ''")
    links = [row['maps_link'] for row in cursor.fetchall()]
    conn.close()
    return set(links)
