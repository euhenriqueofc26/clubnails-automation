import sqlite3
import os

def criar_banco():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'leads.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(leads)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if not columns:
        cursor.execute('''
            CREATE TABLE leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                maps_link TEXT UNIQUE,
                telefone TEXT,
                instagram TEXT,
                cidade TEXT,
                categoria TEXT,
                fonte TEXT,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pendente'
            )
        ''')
        print("Tabela leads criada com sucesso")
    else:
        # Adicionar colunas que faltam
        if 'maps_link' not in columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN maps_link TEXT")
        if 'telefone' not in columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN telefone TEXT")
        if 'instagram' not in columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN instagram TEXT")
        if 'cidade' not in columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN cidade TEXT")
        if 'data_coleta' not in columns:
            cursor.execute("ALTER TABLE leads ADD COLUMN data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("Tabela leads atualizada com sucesso")
    
    conn.commit()
    conn.close()
    print(f"Banco de dados: {db_path}")

if __name__ == '__main__':
    criar_banco()
