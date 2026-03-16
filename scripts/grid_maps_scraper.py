import os
import sys
from playwright.sync_api import sync_playwright
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import log_info, log_sucesso
from utils.database import init_database, salvar_lead

COOKIES_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'cookies.json')

def connect_to_existing_browser():
    """Conecta a um navegador Chrome existente via CDP"""
    init_database()
    
    cdp_url = "http://localhost:9222"
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
            log_info("Conectado ao navegador existente!")
        except Exception as e:
            log_info("Não foi possível conectar ao navegador existente")
            log_info("Iniciando novo navegador...")
            
            browser = p.chromium.launch(
                headless=False,
                args=['--remote-debugging-port=9222']
            )
            
            log_info("=" * 60)
            log_info("FAÇA LOGIN NO GOOGLE MAPS MANUALMENTE")
            log_info("Após login completo, espere 10 segundos")
            log_info("Ai eu rodo o scraping: python scripts/grid_maps_scraper.py")
            log_info("=" * 60)
            
            time.sleep(120)
            
            cookies = browser.cookies
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            
            log_info("Cookies salvos!")
        
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        
        if not page.url or "google.com/maps" not in page.url:
            page.goto("https://www.google.com/maps", wait_until="domcontentloaded")
            time.sleep(5)
        
        page.goto("https://www.google.com/maps/search/nail+designer+S%C3%A3o+Paulo", wait_until="domcontentloaded")
        time.sleep(8)
        
        total_salvo = 0
        seen = set()
        
        for scroll in range(25):
            time.sleep(2)
            
            cards = page.locator('.Nv2PK')
            count = cards.count()
            
            log_info(f"Scroll {scroll+1}: {count} cards")
            
            for j in range(count):
                try:
                    card = cards.nth(j)
                    link_elem = card.locator('a').first
                    nome_elem = card.locator('.qBF1Pd').first
                    
                    if link_elem.count() > 0 and nome_elem.count() > 0:
                        href = link_elem.get_attribute('href')
                        nome = nome_elem.inner_text()
                        
                        if href and nome and href not in seen:
                            seen.add(href)
                            if salvar_lead({'nome': nome, 'link': href}):
                                total_salvo += 1
                                log_info(f"Novo: {nome[:40]}")
                except:
                    continue
            
            if scroll < 24:
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
        
        log_sucesso(f"Total salvo: {total_salvo}")
        
        browser.close()

if __name__ == '__main__':
    connect_to_existing_browser()
