import os, sys, time, random, re
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists

CIDADES = ["São Paulo, SP"]
SEGMENTOS = ["manicure"]

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
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--allow-running-insecure-content',
            '--disable-gpu',
            '--no-zygote',
            '--single-process',
        ]
    )
    
    context = browser.new_context(
        viewport={'width': 1400, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='pt-BR',
        timezone_id='America/Sao_Paulo',
        permissions=['geolocation'],
    )
    
    page = context.new_page()
    
    # Bloqueia recursos pesados
    page.route('**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}', lambda route: route.abort())
    
    try:
        url = f"https://www.google.com/maps/search/{segmento}+{cidade.replace(' ', '+')}"
        print(f"Abrindo: {url}")
        
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        delay(5)
        
        print("Aguardando carregar...")
        
        # Espera aparecer resultados
        page.wait_for_selector('div.Nv2PK, div.section-result', timeout=15000)
        
        print("Scrollando...")
        
        # Scroll
        for _ in range(20):
            page.mouse.wheel(0, 600)
            delay(0.5)
        
        delay(2)
        
        # Pega resultados
        cards = page.query_selector_all('div.Nv2PK')
        
        if not cards:
            cards = page.query_selector_all('div.section-result')
        
        if not cards:
            cards = page.query_selector_all('a[href*="/maps/place/"]')
        
        print(f"Encontrados: {len(cards)}")
        
        for i, card in enumerate(cards[:30]):
            try:
                nome = ''
                telefone = ''
                
                # Nome
                for sel in ['div.fontHeadlineSmall', 'h3', '.section-result-title']:
                    try:
                        el = card.query_selector(sel)
                        if el:
                            nome = el.inner_text().strip()
                            if nome: break
                    except: pass
                
                if not nome: continue
                
                print(f"[{i+1}] {nome[:30]}...", end=" ")
                
                # Clique
                try:
                    card.click()
                    delay(2)
                except: pass
                
                # Telefone
                content = page.content()
                tels = re.findall(r'(?:\+?55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}', content)
                for t in tels[:3]:
                    tel = limpar_telefone(t)
                    if tel and len(tel) >= 10:
                        telefone = tel
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
                
                delay(1)
                
                try: 
                    page.keyboard.press('Escape')
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
    print("COLETA DE LEADS")
    print("="*50)
    
    init_db()
    
    for seg in SEGMENTOS:
        for cid in CIDADES:
            try:
                n = coletar(seg, cid)
                print(f"Total: {get_leads_count()}")
            except Exception as e:
                print(f"Erro: {e}")
                continue
    
    print(f"\nFINAL: {get_leads_count()}")

if __name__ == "__main__":
    run()
