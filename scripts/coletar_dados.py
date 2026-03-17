import os, sys, time, random, re
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists

CIDADES = ["São Paulo, SP", "São Caetano do Sul, SP", "São Bernardo do Campo, SP", "Santo André, SP", "Osasco, SP"]
SEGMENTOS = ["manicure", "studio de unha", "nails designers", "lash design", "unhas em gel", "alongamento de unhas"]

def delay(s=2):
    time.sleep(random.uniform(s, s+1))

def limpar_telefone(t):
    if not t: return ''
    return ''.join(c for c in str(t) if c.isdigit())

def coletar(segmento, cidade):
    print(f"\n>> {segmento} em {cidade}")
    novos = 0
    
    pw = sync_playwright().start()
    
    browser = pw.chromium.launch(
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
        ]
    )
    
    context = browser.new_context(
        viewport={'width': 1400, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    )
    
    page = context.new_page()
    
    try:
        url = f"https://www.google.com/maps/search/{segmento}+{cidade.replace(' ', '+')}"
        print(f"Abrindo: {url}")
        
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        delay(5)
        
        print("Aguardando resultados...")
        
        # Espera resultados
        try:
            page.wait_for_selector('div.Nv2PK', timeout=10000)
        except:
            pass
        
        delay(3)
        
        print("Scrollando...")
        
        # Scroll para carregar mais resultados
        for _ in range(30):
            page.mouse.wheel(0, 500)
            delay(0.3)
        
        delay(2)
        
        # Pega todos os resultados
        cards = page.query_selector_all('div.Nv2PK')
        print(f"Encontrados: {len(cards)} resultados")
        
        for i, card in enumerate(cards):
            try:
                nome = ''
                telefone = ''
                instagram = ''
                endereco = ''
                
                # Pega nome
                try:
                    nome = card.query_selector('div.fontHeadlineSmall').inner_text()
                except:
                    try:
                        nome = card.query_selector('h3').inner_text()
                    except:
                        continue
                
                if not nome: continue
                
                print(f"[{i+1}] {nome[:35]}...", end=" ")
                
                # Clique no card para abrir detalhes
                try:
                    card.click()
                    delay(2.5)
                except:
                    pass
                
                # Pega informações da página
                page_text = page.inner_text()
                
                # Procura telefone
                # Formatos: (11) 99999-9999, 11999999999, +55 11 99999-9999
                telefones = re.findall(
                    r'(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}',
                    page_text
                )
                
                for tel in telefones:
                    tel_limpo = limpar_telefone(tel)
                    if tel_limpo and len(tel_limpo) >= 10:
                        telefone = tel_limpo
                        break
                
                # Procura Instagram
                links = page.query_selector_all('a[href*="instagram"]')
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if href and 'instagram.com' in href:
                            instagram = href
                            break
                    except:
                        pass
                
                # Procura endereço
                try:
                    ends = page.query_selector_all('span[jpo="3"]')
                    if ends:
                        endereco = ends[0].inner_text()
                except:
                    pass
                
                if telefone:
                    if lead_exists(telefone):
                        print(f"dup")
                    else:
                        add_lead(nome, telefone, endereco, segmento, f"GM-{cidade}", instagram)
                        novos += 1
                        print(f"✓ {telefone} | Insta: {instagram[:20] if instagram else '-'}")
                else:
                    print(f"sem tel")
                
                delay(1.5)
                
                # Fecha popup
                try:
                    page.keyboard.press('Escape')
                except:
                    pass
                delay(0.5)
                    
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
                print(f"\nParcial: {get_leads_count()} leads | Novos: {total}")
            except Exception as e:
                print(f"Erro: {e}")
                continue
    
    print(f"\n{'='*50}")
    print(f"FINAL: {get_leads_count()} leads")
    print("="*50)

if __name__ == "__main__":
    run()
