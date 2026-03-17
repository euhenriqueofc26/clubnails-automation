import os, sys, time, random, re
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists

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
    browser = pw.chromium.launch(headless=False, args=['--start-maximized'])
    page = browser.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    
    try:
        url = f"https://www.google.com/maps/search/{segmento}+{cidade}"
        print(f"Abrindo: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        delay(5)
        
        print("Scrollando...")
        
        # Scroll lento e gradual
        for scrol in range(25):
            page.mouse.wheel(0, random.randint(800, 1200))
            delay(0.8)
            
            # Tenta carregar mais resultados
            try:
                mais = page.query_selector('button:has-text("Mais resultados")')
                if mais and mais.is_visible():
                    mais.click()
                    delay(1)
            except:
                pass
        
        delay(3)
        
        # Pega todos os resultados
        selectors = [
            'div.Nv2PK',
            'div[data-cel-id]', 
            'a[href*="/maps/place/"]',
            '.section-result'
        ]
        
        cards = []
        for sel in selectors:
            cards = page.query_selector_all(sel)
            if len(cards) > 5:
                print(f"Encontrados: {len(cards)} com seletor: {sel}")
                break
        
        print(f"Total de cards: {len(cards)}")
        
        for i, card in enumerate(cards[:50]):
            try:
                nome = ''
                telefone = ''
                
                # Tenta várias formas de pegar o nome
                for sel_nome in ['div.fontHeadlineSmall', 'h3', 'div.section-result-title', 'span']:
                    try:
                        el = card.query_selector(sel_nome)
                        if el:
                            nome = el.inner_text().strip()
                            if nome and len(nome) > 2:
                                break
                    except:
                        pass
                
                if not nome or len(nome) < 3:
                    continue
                
                print(f"[{i+1}] {nome[:30]}...", end=" ")
                
                # Clica no card
                try:
                    card.click()
                    delay(2.5)
                except:
                    pass
                
                # Procura telefone na página
                content = page.content()
                
                # Regex para telefones brasileiros
                tels = re.findall(r'(?:\+?55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}', content)
                for t in tels[:5]:
                    tel_limpo = limpar_telefone(t)
                    if tel_limpo and len(tel_limpo) >= 10:
                        telefone = tel_limpo
                        break
                
                if telefone:
                    if lead_exists(telefone):
                        print("dup")
                    else:
                        add_lead(nome, telefone, '', segmento, f"GM-{cidade}")
                        novos += 1
                        print(f"✓ {telefone}")
                else:
                    print("sem tel")
                
                delay(1.5)
                
                #Fecha popup
                try:
                    page.keyboard.press('Escape')
                    delay(0.5)
                except:
                    pass
                    
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
                print(f"Total: {get_leads_count()} | Novos: {n}")
            except Exception as e:
                print(f"Erro: {e}")
                continue
    
    print(f"\nFINAL: {get_leads_count()} leads")

if __name__ == "__main__":
    run()
