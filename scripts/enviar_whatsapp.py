import os
import time
import random
import webbrowser
from datetime import datetime
from urllib.parse import quote
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import get_all_leads

def delay(min_sec=1, max_sec=2):
    time.sleep(random.uniform(min_sec, max_sec))

def ler_mensagem(arquivo='mensagens/mensagem_padrao.txt'):
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    return "Olá! vim através do WhatsApp para falar sobre nossos serviços de Unhas."

def enviar_whatsapp(limite=30, pausa=60):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando envio de mensagens...")
    
    leads = get_all_leads()
    mensagem = ler_mensagem()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mensagem: {mensagem[:50]}...")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Total de leads: {len(leads)}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Limite: {limite} | Pausa: {pausa}s")
    
    enviada = 0
    
    for i, lead in enumerate(leads[:limite]):
        telefone = lead['telefone']
        nome = lead['nome']
        
        if not telefone or telefone == "sem telefone":
            print(f"[{i+1}] Pulando {nome} - sem telefone")
            continue
        
        telefone_limpo = ''.join(c for c in str(telefone) if c.isdigit())
        
        if not telefone_limpo.startswith('55'):
            telefone_limpo = '55' + telefone_limpo
        
        mensagem_personalizada = mensagem.replace('{nome}', nome)
        
        url_whatsapp = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={quote(mensagem_personalizada)}"
        
        print(f"[{enviada+1}/{limite}] Enviando para {nome} ({telefone_limpo})...")
        
        webbrowser.open(url_whatsapp)
        
        delay(1, 2)
        
        enviada += 1
        
        if enviada < limite:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando {pausa}s...")
            time.sleep(pausa)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Envio finalizado! {enviada} mensagens enviadas.")
    return enviada

if __name__ == "__main__":
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    pausa = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    enviar_whatsapp(limite, pausa)
