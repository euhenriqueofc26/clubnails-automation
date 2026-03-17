import os
import sys
import time
import random
import webbrowser
from datetime import datetime
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import get_all_leads, get_leads_count

def delay(min_sec=1, max_sec=2):
    time.sleep(random.uniform(min_sec, max_sec))

def ler_mensagem(arquivo='mensagens/mensagem_padrao.txt'):
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    return "Olá! Vim através do WhatsApp para falar sobre nossos serviços."

def formatar_telefone(telefone):
    if not telefone:
        return None
    
    tel = ''.join(c for c in str(telefone) if c.isdigit())
    
    if not tel:
        return None
    
    if tel.startswith('0'):
        tel = tel[1:]
    
    if not tel.startswith('55'):
        tel = '55' + tel
    
    if len(tel) >= 12:
        return tel
    
    return None

def enviar_whatsapp(limite=30, pausa=60, segmentos=None):
    print(f"\n{'='*60}")
    print(f"ENVIO DE MENSAGENS WHATSAPP - CLUB NAILS BRASIL")
    print(f"{'='*60}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    leads = get_all_leads()
    
    if segmentos:
        leads = [l for l in leads if l['segmento'] in segmentos]
    
    mensagem = ler_mensagem()
    
    print(f"Mensagem: {mensagem[:80]}...")
    print(f"Total de leads: {len(leads)}")
    print(f"Limite: {limite} | Pausa: {pausa}s")
    print(f"{'='*60}\n")
    
    enviadas = 0
    falhas = 0
    
    for i, lead in enumerate(leads[:limite]):
        nome = lead['nome']
        telefone = lead['telefone']
        
        tel_formatado = formatar_telefone(telefone)
        
        if not tel_formatado:
            print(f"[{i+1}/{limite}] ❌ Sem telefone: {nome}")
            falhas += 1
            continue
        
        msg_personalizada = mensagem.replace('{nome}', nome)
        msg_formatada = quote(msg_personalizada)
        
        url_wa = f"https://web.whatsapp.com/send?phone={tel_formatado}&text={msg_formatada}"
        
        print(f"[{enviadas+1}/{limite}] 📱 Enviando para: {nome}")
        print(f"    Tel: {tel_formatado}")
        
        try:
            webbrowser.open(url_wa)
            delay(1, 2)
            
            enviadas += 1
            
            if enviadas < limite:
                print(f"    ⏳ Aguardando {pausa}s...")
                time.sleep(pausa)
                
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            falhas += 1
    
    print(f"\n{'='*60}")
    print(f"ENVIO FINALIZADO!")
    print(f"Mensagens enviadas: {enviadas}")
    print(f"Falhas: {falhas}")
    print(f"{'='*60}")
    
    return enviadas

def listar_leads():
    print(f"\n{'='*60}")
    print(f"LEADS COLETADOS")
    print(f"{'='*60}")
    
    leads = get_all_leads()
    total = len(leads)
    
    print(f"Total de leads: {total}\n")
    
    if total == 0:
        print("Nenhum lead coletado ainda!")
        print("Execute: python scripts/coletar_dados.py")
        return
    
    for i, lead in enumerate(leads[:20]):
        print(f"[{i+1}] {lead['nome']}")
        print(f"    Tel: {lead['telefone'] or 'N/A'}")
        print(f"    Insta: {lead['instagram'] or 'N/A'}")
        print(f"    Segmento: {lead['segmento']}")
        print(f"    Fonte: {lead['fonte']}")
        print()
    
    if total > 20:
        print(f"... e mais {total - 20} leads")
    
    print(f"\nPara exportar: python scripts/exportar_contatos.py")

if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "listar"
    
    if acao == "listar":
        listar_leads()
    elif acao == "enviar":
        limite = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        pausa = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        enviar_whatsapp(limite, pausa)
    elif acao == "segmento":
        segmento = sys.argv[2] if len(sys.argv) > 2 else "Unhas"
        limite = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        pausa = int(sys.argv[4]) if len(sys.argv) > 4 else 60
        enviar_whatsapp(limite, pausa, [segmento])
    else:
        print("Uso:")
        print("  python scripts/enviar_whatsapp.py listar")
        print("  python scripts/enviar_whatsapp.py enviar 30 60")
        print("  python scripts/enviar_whatsapp.py segmento 'Unhas' 30 60")
