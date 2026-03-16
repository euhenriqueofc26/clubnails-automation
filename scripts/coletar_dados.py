import os
import sys
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count, lead_exists, DB_PATH

CIDADES_SP = [
    "São Paulo, SP",
    "São Caetano do Sul, SP",
    "São Bernardo do Campo, SP",
    "Santo André, SP",
    "Osasco, SP",
    "Guarulhos, SP",
    "Campinas, SP",
    "Santos, SP",
    "São José dos Campos, SP",
    "Ribeirão Preto, SP",
    "Sorocaba, SP",
    "Mauá, SP",
    "Mogi das Cruzes, SP",
    "Diadema, SP",
    "Carapicuíba, SP",
    "Cotia, SP",
    "Itaquaquecetuba, SP",
    "Suzano, SP",
    "Poá, SP",
    "Ferraz de Vasconcelos, SP"
]

SEGMENTOS = [
    "nails designers",
    "manicure",
    "studio de unha",
    "lash design",
    "Nail Designers",
    "unhas em gel",
    "alongamento de unhas",
    "esmaltaria",
    "studio manicure",
    "salão de beleza",
    "unhas decoradas",
    "manicure e pedicure",
    "beleza e estética",
    "studio beleza",
    "espaço uñas"
]

def delay(min_sec=1, max_sec=2):
    time.sleep(random.uniform(min_sec, max_sec))

def limpar_telefone(tel):
    if not tel:
        return ''
    return ''.join(c for c in str(tel) if c.isdigit())

def coletar_segmento_cidade(segmento, cidade, max_leads=100):
    print(f"\n  >> {segmento} em {cidade}...")
    
    total_novos = 0
    duplicados = 0
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    try:
        search = f"{segmento} {cidade}"
        url = f"https://www.google.com/maps/search/{search.replace(' ', '+')}"
        
        page.goto(url, wait_until="networkidle", timeout=60000)
        delay(3, 5)
        
        scrolls = 0
        max_scrolls = 30
        
        while scrolls < max_scrolls:
            page.mouse.wheel(0, random.randint(2000, 3000))
            delay(1, 2)
            scrolls += 1
            
            try:
                mais = page.locator('button:has-text("Mais resultados")')
                if mais.is_visible():
                    mais.click()
                    delay(1, 2)
            except:
                pass
        
        delay(2, 3)
        
        listings = page.locator('a[href*="/maps/place/"]').all()
        print(f"    Encontrados {len(listings)} links")
        
        for listing in listings[:max_leads]:
            try:
                href = listing.get_attribute('href')
                if not href or '/maps/place/' not in href:
                    continue
                
                page.goto(href, wait_until="networkidle", timeout=30000)
                delay(2, 3)
                
                nome = ''
                try:
                    nome = page.locator('h1').inner_text(timeout=5000)
                except:
                    pass
                
                if not nome:
                    try:
                        nome = page.locator('div[data-item-id="title"]').inner_text(timeout=3000)
                    except:
                        continue
                
                telefone = ''
                instagram = ''
                site = ''
                endereco = ''
                
                botoes_tel = page.locator('button[aria-label*="Telefone"], button[aria-label*="Phone"]').all()
                for btn in botoes_tel[:3]:
                    try:
                        btn.click()
                        delay(1, 1.5)
                        tel_text = btn.inner_text()
                        if any(c.isdigit() for c in tel_text):
                            telefone = limpar_telefone(tel_text)
                            break
                    except:
                        pass
                
                if not telefone:
                    spans = page.locator('span').all()
                    for span in spans[:50]:
                        try:
                            txt = span.inner_text()
                            if len(txt) >= 10 and len(txt) <= 15 and txt.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
                                telefone = limpar_telefone(txt)
                                break
                        except:
                            pass
                
                links = page.locator('a[href*="instagram.com"]').all()
                for link in links[:3]:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            instagram = href
                            break
                    except:
                        pass
                
                if not instagram:
                    links = page.locator('a').all()
                    for link in links[:30]:
                        try:
                            txt = link.inner_text().lower()
                            if 'instagram' in txt or (txt.startswith('@') and len(txt) > 3):
                                href = link.get_attribute('href')
                                if href and 'http' in href:
                                    instagram = href
                                    break
                        except:
                            pass
                
                try:
                    ends = page.locator('span[jpo="3"]').all()
                    if ends:
                        endereco = ends[0].inner_text()
                except:
                    pass
                
                if nome and telefone:
                    if lead_exists(telefone):
                        duplicados += 1
                        print(f"    Duplicado: {nome[:30]}...")
                        continue
                    
                    add_lead(nome, telefone, endereco, segmento, f"Google Maps - {cidade}", instagram)
                    total_novos += 1
                    print(f"    ✓ {nome[:35]}... - {telefone}")
                elif nome:
                    print(f"    - {nome[:35]}... (sem telefone)")
                
                delay(1, 2)
                
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"    Erro: {e}")
    
    finally:
        try:
            browser.close()
        except:
            pass
        try:
            playwright.stop()
        except:
            pass
    
    return total_novos, duplicados

def run_full_collection():
    print(f"\n{'#'*60}")
    print("# COLETA DE LEADS - CLUB NAILS BRASIL")
    print(f"# Sem duplicatas - Apenas telefones únicos")
    print(f"{'#'*60}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    init_db()
    
    total_novos = 0
    total_duplicados = 0
    
    for segmento in SEGMENTOS:
        for cidade in CIDADES_SP:
            try:
                novos, dup = coletar_segmento_cidade(segmento, cidade, max_leads=80)
                total_novos += novos
                total_duplicados += dup
                
                atual = get_leads_count()
                print(f"\n    >> Total: {atual} leads | Novos: {total_novos} | Duplicados: {total_duplicados}")
                
            except Exception as e:
                print(f"    Erro em {segmento}/{cidade}: {e}")
                continue
    
    print(f"\n{'#'*60}")
    print(f"COLETA FINALIZADA!")
    print(f"Total novos: {total_novos}")
    print(f"Total duplicados ignorados: {total_duplicados}")
    print(f"Total no banco: {get_leads_count()}")
    print(f"{'#'*60}")

if __name__ == "__main__":
    run_full_collection()
