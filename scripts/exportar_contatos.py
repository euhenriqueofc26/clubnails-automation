import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'leads.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'contatos.csv')

def clean_phone(phone):
    if not phone:
        return None
    nums = ''.join(c for c in str(phone) if c.isdigit())
    if len(nums) >= 10:
        return nums
    return None

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

rows = c.execute("""
    SELECT nome, telefone
    FROM leads
    WHERE telefone IS NOT NULL AND telefone != ''
""").fetchall()

contatos_validos = []
for nome, telefone in rows:
    telefone_limpo = clean_phone(telefone)
    if telefone_limpo:
        contatos_validos.append((nome, telefone_limpo))

unique_contacts = {}
for nome, telefone in contatos_validos:
    if telefone not in unique_contacts:
        unique_contacts[telefone] = nome

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["nome", "telefone"])
    for telefone, nome in unique_contacts.items():
        writer.writerow([nome, telefone])

conn.close()

print(f"Arquivo {OUTPUT_PATH} gerado com sucesso.")
print(f"Total de contatos exportados: {len(unique_contacts)}")
