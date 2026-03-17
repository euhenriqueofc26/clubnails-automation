import os
import sys
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists, DB_PATH

CIDADES = [
    "São Paulo, SP",
    "São Caetano do Sul, SP",
    "São Bernardo do Campo, SP",
    "Santo André, SP",
    "Osasco, SP",
    "Guarulhos, SP",
    "Campinas, SP"
]

SEGMENTOS = [
    "nails designers",
    "manicure", 
    "studio de unha",
    "lash design",
    "unhas em gel",
    "alongamento de unhas",
    "esmaltaria"
]

def delay(s=1):
    time.sleep(random.uniform(s, s+1))

def limpar_telefone(tel):
    if not tel:
        return ''
    return ''.join(c for c in str(tel) if c.isdigit())

def coletar(segmento, cidade, max_leads=50):
    print(f"\n>> {segmento} em {cidade}")
    
    novos = 0
    dup = 0
    
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
        url = f"https://www.google.com/maps/search/{segmento}+{cidade}"
        print(f"Abrindo: {url}")
        page.goto(url)
        delay(5)
        
        print("Procurando resultados...")
        
        for _ in range(15):
            page.mouse.wheel(0, 2000)
            delay(1)
        
        delay(3)
        
        cards = page.query_selector_all('div[role="article"]')
        print(f"Encontrados {len(cards)} resultados")
        
        for i, card in enumerate(cards[:max_leads]):
            try:
                nome = ''
                telefone = ''
                instagram = ''
                endereco = ''
                
                try:
                    nome_elem = card.query_selector('div.fontTitleSmall')
                    if nome_elem:
                        nome = nome_elem.inner_text()
                except:
                    pass
                
                if not nome:
                    continue
                
                print(f"[{i+1}] {nome[:30]}...")
                
                try:
                    card.click()
                    delay(2)
                except:
                    pass
                
                page_content = page.content()
                
                import re
                tels = re.findall(r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}', page_content)
                for tel in tels:
                    if len(tel.replace(' ','').replace('-','').replace('(','').replace(')','')) >= 10:
                        telefone = limpar_telefone(tel)
                        break
                
                instas = re.findall(r'instagram\.com/[\w\.]+', page_content)
                if instas:
                    instagram = 'https://' + instas[0]
                
                if telefone:
                    if lead_exists(telefone):
                        dup += 1
                        print(f"  duplicado")
                        continue
                    
                    add_lead(nome, telefone, endereco, segmento, f"Google Maps - {cidade}", instagram)
                    novos += 1
                    print(f"  ✓ {telefone}")
                else:
                    print(f"  sem telefone")
                
                delay(1)
                
                try:
                    page.keyboard.press('Escape')
                except:
                    pass
                    
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"Erro: {e}")
    
    finally:
        try:
            browser.close()
        except:
            pass
        try:
            pw.stop()
        except:
            pass
    
    return novos, dup

def run():
    print("\n" + "="*50)
    print("COLETA DE LEADS - CLUB NAILS")
    print("="*50)
    print(f"Inicio: {datetime.now()}")
    
    init_db()
    
    total_novos = 0
    total_dup = 0
    
    for seg in SEGMENTOS:
        for cid in CIDADES:
            try:
                n, d = coletar(seg, cid, 50)
                total_novos += n
                total_dup += d
                print(f"\nTotal: {get_leads_count()} | Nov: {total_novos} | Dup: {total_dup}")
            except Exception as e:
                print(f"Erro em {seg}/{cid}: {e}")
                continue
    
    print("\n" + "="*50)
    print(f"FINALIZADO! Total: {get_leads_count()}")
    print("="*50)

if __name__ == "__main__":
    run()
