import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'execucao.log')

def clean_message(msg):
    if msg is None:
        return "None"
    return str(msg).encode('utf-8', errors='replace').decode('utf-8', errors='replace')

def log(mensagem, nivel="INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clean_msg = clean_message(mensagem)
    log_entry = f"[{timestamp}] [{nivel}] {clean_msg}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    try:
        print(f"[{timestamp}] [{nivel}] {clean_msg}", flush=True)
    except Exception:
        print(f"[{timestamp}] [{nivel}] {clean_msg.encode('ascii', errors='replace').decode('ascii')}", flush=True)

def log_info(mensagem):
    log(mensagem, "INFO")

def log_erro(mensagem):
    log(mensagem, "ERRO")

def log_sucesso(mensagem):
    log(mensagem, "SUCESSO")

def log_warning(mensagem):
    log(mensagem, "AVISO")

def log_separator():
    log("=" * 60)
