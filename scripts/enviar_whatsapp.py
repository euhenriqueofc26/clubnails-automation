import csv
import time
import webbrowser
import urllib.parse
import os
from datetime import datetime

MENSAGEM = """Bom dia, Tudo bem?

Estamos convidando nails para fazer parte do evento das 10 fundadoras da ClubNailsBrasil

https://www.clubnailsbrasil.com.br/fundadoras

Dê uma olhadinha com carinho e vem fazer parte desse lançamento!

Venha ser uma fundadora. O movimento pode parecer pequeno, mas todo grande movimento começou justamente assim... como ondas até se tornarem gigantes.

Ainda irei te conquistar 😁

Tenha uma ótima noite e muitas clientes!"""

mensagem_formatada = urllib.parse.quote(MENSAGEM)

LIMITE_POR_DIA = 30
INTERVALO = 60

CONTATOS_PATH = os.path.join(os.path.dirname(__file__), '..', 'contatos.csv')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'whatsapp.log')

def log(mensagem):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    texto = f"[{timestamp}] {mensagem}"
    print(texto)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(texto + '\n')

def clean_phone(telefone):
    if not telefone:
        return None
    nums = ''.join(c for c in str(telefone) if c.isdigit())
    if len(nums) >= 10:
        return nums
    return None

def format_phone_br(telefone):
    telefone = clean_phone(telefone)
    if not telefone:
        return None
    if len(telefone) == 10 or len(telefone) == 11:
        return '55' + telefone
    return '55' + telefone

def iniciar_envio():
    if not os.path.exists(CONTATOS_PATH):
        log(f"ERRO: Arquivo {CONTATOS_PATH} não encontrado.")
        log("Execute primeiro: python scripts/exportar_contatos.py")
        return
    
    with open(CONTATOS_PATH, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contatos = list(reader)
    
    log(f"Iniciando envio - {len(contatos)} contatos disponíveis")
    log(f"Limite: {LIMITE_POR_DIA} por dia | Intervalo: {INTERVALO} segundos")
    log("-" * 50)
    
    contador = 0
    
    for row in contatos:
        if contador >= LIMITE_POR_DIA:
            log(f"Limite diário atingido ({LIMITE_POR_DIA} contatos)")
            break
        
        nome = row.get('nome', '').strip()
        telefone = clean_phone(row.get('telefone', ''))
        
        if not telefone:
            log(f"SKIP: Telefone inválido - {nome}")
            continue
        
        telefone_formatado = format_phone_br(telefone)
        link = f"https://wa.me/{telefone_formatado}?text={mensagem_formatada}"
        
        webbrowser.open(link)
        contador += 1
        
        log(f"[{contador}/{LIMITE_POR_DIA}] Aberta conversa: {nome} ({telefone})")
        
        if contador < LIMITE_POR_DIA:
            log(f"Aguardando {INTERVALO} segundos...")
            time.sleep(INTERVALO)
    
    log("-" * 50)
    log(f"ENVIO CONCLUÍDO: {contador} conversas abertas hoje")
    log("Próximo envio: rode o script novamente amanhã")

if __name__ == '__main__':
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    iniciar_envio()
