import os
import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import add_lead, init_db

def delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def coletar_leads_mapa(business_type="Studios de unhas", location="São Paulo, SP", num_results=50):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando coleta de {business_type} em {location}...")
    
    init_db()
    
    leads_coletados = 0
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        search_url = f"https://www.google.com/maps/search/{business_type.replace(' ', '+')}+em+{location.replace(' ', '+')}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Abrindo: {search_url}")
        
        page.goto(search_url)
        delay(3, 5)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Rolando a página para carregar resultados...")
        
        scroll_count = 0
        max_scrolls = 15
        
        while scroll_count < max_scrolls:
            page.mouse.wheel(0, 2000)
            delay(1, 2)
            scroll_count += 1
            
            try:
                mais_resultados = page.locator('button:has-text("Mais resultados")')
                if mais_resultados.is_visible():
                    mais_resultados.click()
                    delay(2, 3)
            except:
                pass
        
        delay(2, 3)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Extraindo informações dos estabelecimentos...")
        
        listings = page.locator('//div[contains(@class, "Nv2PK")]').all()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Encontrados {len(listings)} estabelecimentos")
        
        for i, listing in enumerate(listings[:num_results]):
            try:
                nome = listing.locator('.fontHeadlineSmall').inner_text(timeout=2000)
            except:
                nome = "Nome não encontrado"
            
            try:
                telefone = ""
                info_text = listing.locator('.fontBodyMedium').inner_text()
                if "Ver número" in info_text or "Telefone" in info_text:
                    telefone_btns = listing.locator('button[aria-label*="Telefone"]')
                    if telefone_btns.count() > 0:
                        telefone_btns.first.click()
                        delay(0.5, 1)
                        telefone = listing.locator('.fontBodyMedium span[data-material="tel"]').inner_text(timeout=1000)
            except:
                telefone = ""
            
            try:
                endereco = listing.locator('.fontBodyMedium span:jepo-contains(".")').first.inner_text(timeout=1000)
            except:
                endereco = ""
            
            if nome and nome != "Nome não encontrado":
                print(f"[{i+1}] {nome} - {telefone}")
                add_lead(nome, telefone, endereco, business_type)
                leads_coletados += 1
                
            delay(0.5, 1.5)
        
        browser.close()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coleta finalizada! {leads_coletados} leads adicionados ao banco.")
    return leads_coletados

if __name__ == "__main__":
    import sys
    negocio = sys.argv[1] if len(sys.argv) > 1 else "Studios de unhas"
    local = sys.argv[2] if len(sys.argv) > 2 else "São Paulo, SP"
    коли = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    coletar_leads_mapa(negocio, local, коли)
