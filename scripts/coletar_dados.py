import os
import sys
import time
import random
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db, get_leads_count

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
    "Ferraz de Vasconcelos, SP",
    "São Caetano do Sul, SP"
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
    " manicure e pedicure",
    "beleza e estética"
]

def delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def init_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled', '--start-maximized']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    return playwright, browser, context

def scroll_page(page, max_scrolls=20):
    print(f"    Rolando página ({max_scrolls} scrolls)...")
    for _ in range(max_scrolls):
        page.mouse.wheel(0, random.randint(1500, 2500))
        delay(0.5, 1)
        
        try:
            mais_btn = page.locator('button:has-text("Mais resultados")')
            if mais_btn.is_visible():
                mais_btn.click()
                delay(1, 2)
        except:
            pass

def extract_lead_details(page, nome):
    lead = {
        'nome': nome,
        'telefone': '',
        'endereco': '',
        'instagram': '',
        'site': '',
        'nota': '',
        'segmento': ''
    }
    
    try:
        delay(1, 2)
        
        info_divs = page.locator('div[data-item-info]').all()
        for div in info_divs:
            try:
                texto = div.inner_text()
                if 'telefone' in texto.lower() or 'whatsapp' in texto.lower():
                    spans = div.locator('span').all()
                    for span in spans:
                        t = span.inner_text()
                        if any(c.isdigit() for c in t) and len(t) > 8:
                            lead['telefone'] = t
                            break
            except:
                pass
        
        links = page.locator('a[href*="instagram"]').all()
        for link in links:
            try:
                href = link.get_attribute('href')
                if href and 'instagram' in href.lower():
                    lead['instagram'] = href
                    break
            except:
                pass
        
        if not lead['instagram']:
            links = page.locator('a').all()
            for link in links:
                try:
                    texto = link.inner_text().lower()
                    if 'instagram' in texto or '@' in texto:
                        href = link.get_attribute('href')
                        if href:
                            lead['instagram'] = href
                            break
                except:
                    pass
        
        links = page.locator('a[href*="website"]').all()
        for link in links:
            try:
                href = link.get_attribute('href')
                if href:
                    lead['site'] = href
                    break
            except:
                pass
        
        try:
            nota = page.locator('span.fontTitleSmall').inner_text()
            if nota:
                lead['nota'] = nota
        except:
            pass
        
        try:
            enderecos = page.locator('span[jpo="3"]').all()
            if enderecos:
                lead['endereco'] = enderecos[0].inner_text()
        except:
            pass
            
    except Exception as e:
        print(f"    Erro ao extrair detalhes: {e}")
    
    return lead

def collect_from_maps(segmento, cidade, max_leads=100):
    print(f"\n{'='*50}")
    print(f"Coletando: {segmento} em {cidade}")
    print(f"{'='*50}")
    
    init_db()
    leads_coletados = 0
    
    try:
        playwright, browser, context = init_browser()
        page = context.new_page()
        
        search = f"{segmento} em {cidade}"
        url = f"https://www.google.com/maps/search/{search.replace(' ', '+')}"
        
        print(f"  Abrindo: {url}")
        page.goto(url, wait_until="networkidle")
        delay(3, 5)
        
        scroll_page(page, max_scrolls=25)
        
        listings = page.locator('div[role="article"]').all()
        print(f"  Encontrados: {len(listings)} estabelecimentos")
        
        for i, listing in enumerate(listings[:max_leads]):
            try:
                nome = ""
                try:
                    nome = listing.locator('div.fontTitleSmall').inner_text(timeout=2000)
                except:
                    try:
                        nome = listing.locator('h3').inner_text(timeout=2000)
                    except:
                        continue
                
                if not nome:
                    continue
                
                print(f"  [{i+1}] {nome[:40]}...")
                
                try:
                    listing.click()
                    delay(2, 3)
                except:
                    pass
                
                lead = extract_lead_details(page, nome)
                lead['segmento'] = segmento
                lead['fonte'] = f"Google Maps - {cidade}"
                
                print(f"      Tel: {lead['telefone'][:20] if lead['telefone'] else 'N/A'}")
                print(f"      Insta: {lead['instagram'][:30] if lead['instagram'] else 'N/A'}")
                
                add_lead(
                    lead['nome'],
                    lead['telefone'],
                    lead['endereco'],
                    lead['segmento'],
                    lead['fonte']
                )
                
                leads_coletados += 1
                
                delay(1, 2)
                
                try:
                    page.keyboard.press('Escape')
                    delay(0.5, 1)
                except:
                    pass
                    
            except Exception as e:
                print(f"    Erro: {e}")
                continue
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"  Erro geral: {e}")
    
    return leads_coletados

def run_full_collection():
    print(f"\n{'#'*60}")
    print("# COLETA COMPLETA DE LEADS - CLUB NAILS BRASIL")
    print(f"{'#'*60}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Segmentos: {len(SEGMENTOS)}")
    print(f"Cidades: {len(CIDADES_SP)}")
    
    init_db()
    
    total_geral = 0
    
    for segmento in SEGMENTOS:
        for cidade in CIDADES_SP:
            try:
                total = collect_from_maps(segmento, cidade, max_leads=50)
                total_geral += total
                
                atual = get_leads_count()
                print(f"\n  >> Total acumulado: {atual} leads")
                
            except Exception as e:
                print(f"Erro em {segmento}/{cidade}: {e}")
                continue
    
    print(f"\n{'#'*60}")
    print(f"COLETA FINALIZADA!")
    print(f"Total de leads coletados: {total_geral}")
    print(f"Total no banco: {get_leads_count()}")
    print(f"{'#'*60}")

if __name__ == "__main__":
    run_full_collection()
