import os, sys, time, random, re
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists, DB_PATH

CIDADES = ["São Paulo, SP", "São Caetano do Sul, SP", "São Bernardo do Campo, SP"]
SEGMENTOS = ["manicure", "studio de unha", "nails designers"]

def delay(s=2):
    time.sleep(random.uniform(s, s+1))

def limpar_telefone(t):
    if not t: return ''
    return ''.join(c for c in str(t) if c.isdigit())

def coletar(segmento, cidade):
    print(f"\n>> {segmento} em {cidade}")
    novos = 0
    
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
        url = f"https://www.google.com/maps/search/{segmento}+{cidade}"
        page.goto(url)
        delay(5)
        
        for _ in range(10):
            page.mouse.wheel(0, 1500)
            delay(1)
        
        delay(2)
        
        cards = page.query_selector_all('div.Nv2PK')
        print(f"Encontrados: {len(cards)}")
        
        for i, card in enumerate(cards[:30]):
            try:
                nome = ''
                telefone = ''
                
                try:
                    nome = card.query_selector('div.fontHeadlineSmall').inner_text()
                except:
                    try:
                        nome = card.query_selector('span.jxcore').inner_text()
                    except:
                        continue
                
                if not nome: continue
                
                print(f"[{i+1}] {nome[:35]}...", end=" ")
                
                try:
                    card.click()
                    delay(2)
                except: pass
                
                content = page.content()
                
                tels = re.findall(r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}', content)
                for t in tels[:3]:
                    if len(limpar_telefone(t)) >= 10:
                        telefone = limpar_telefone(t)
                        break
                
                if telefone:
                    if lead_exists(telefone):
                        print("duplicado")
                    else:
                        add_lead(nome, telefone, '', segmento, f"GM-{cidade}")
                        novos += 1
                        print(f"✓ {telefone}")
                else:
                    print("sem tel")
                
                delay(1)
                try: page.keyboard.press('Escape')
                except: pass
                    
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        try: browser.close()
        except: pass
        try: pw.stop()
        except: pass
    
    return novos

def run():
    print("\n" + "="*50)
    print("COLETA DE LEADS - CLUB NAILS")
    print("="*50)
    
    init_db()
    
    total = 0
    for seg in SEGMENTOS:
        for cid in CIDADES:
            try:
                n = coletar(seg, cid)
                total += n
                print(f"Total: {get_leads_count()}")
            except Exception as e:
                print(f"Erro: {e}")
                continue
    
    print(f"\nFINAL: {get_leads_count()} leads")

if __name__ == "__main__":
    run()
