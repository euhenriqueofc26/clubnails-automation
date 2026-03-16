import os
import sys
import json
import time
import re
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import log_info, log_sucesso, log_erro
from utils.database import init_database, salvar_lead, get_all_maps_links

CIDADES = [
    "São Paulo",
    "São Caetano do Sul",
    "São Bernardo do Campo",
    "Santo André",
    "Osasco",
    "Guarulhos"
]

BUSCAS = [
    "nail designer",
    "manicure",
    "salão de unhas",
    "studio unhas",
    "alongamento de unha"
]

USER_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'chrome_user_data')
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), '..', 'checkpoint.json')

def save_checkpoint(cidade_idx, busca_idx):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({'cidade_idx': cidade_idx, 'busca_idx': busca_idx}, f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'cidade_idx': 0, 'busca_idx': 0}

def get_phone_from_profile(page):
    page.mouse.wheel(0, 200)
    time.sleep(0.3)
    
    try:
        links = page.locator('a[href^="tel:"]')
        if links.count() > 0:
            href = links.first.get_attribute('href')
            if href:
                phone = re.sub(r'\D', '', href.replace('tel:', ''))
                if len(phone) >= 10:
                    return phone
    except:
        pass
    
    try:
        content = page.content()
        patterns = [r'\+55\s?\d{2}\s?\d{4,5}\s?\d{4}', r'\(?\d{2}\)?\s?\d{4,5}[\s-]?\d{4}']
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                numbers = re.sub(r'\D', '', match)
                if len(numbers) >= 10:
                    return numbers
    except:
        pass
    
    return None

def get_instagram_from_profile(page):
    try:
        links = page.locator('a')
        for i in range(min(links.count(), 30)):
            try:
                href = links.nth(i).get_attribute('href')
                if href and 'instagram.com' in href:
                    match = re.search(r'instagram\.com/([^/?]+)', href)
                    if match:
                        return match.group(1)
            except:
                continue
    except:
        pass
    return None

def process_card_fast(page, card):
    try:
        nome = card.locator('.qBF1Pd, .fontHeadlineSmall').first.inner_text()
    except:
        return None
    
    try:
        card.locator('a').first.click()
        time.sleep(1)
    except:
        return None
    
    maps_link = page.url
    telefone = get_phone_from_profile(page)
    instagram = get_instagram_from_profile(page)
    
    if telefone:
        telefone = re.sub(r'\D', '', telefone)
        if len(telefone) < 10:
            telefone = None
    
    try:
        page.go_back()
        time.sleep(0.5)
    except:
        pass
    
    return {
        'nome': nome,
        'maps_link': maps_link,
        'telefone': telefone,
        'instagram': instagram
    }

def run_scraper():
    init_database()
    
    existing_links = get_all_maps_links()
    log_info(f"Leads existentes: {len(existing_links)}")
    
    checkpoint = load_checkpoint()
    cidade_idx = checkpoint.get('cidade_idx', 0)
    busca_idx = checkpoint.get('busca_idx', 0)
    
    log_info(f"Iniciando a partir de: cidade {cidade_idx}, busca {busca_idx}")
    
    with sync_playwright() as p:
        context = None
        
        if os.path.exists(USER_DATA_DIR):
            try:
                context = p.chromium.launch_persistent_context(
                    USER_DATA_DIR,
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled'],
                )
                log_info("Browser com user data!")
            except:
                context = None
        
        if context is None:
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled'],
            )
            context = browser.new_context()
            log_info("Browser novo!")
        
        page = context.pages[0] if context.pages else context.new_page()
        
        total_salvo = 0
        
        for i, cidade in enumerate(CIDADES):
            if i < cidade_idx:
                continue
                
            for j, busca in enumerate(BUSCAS):
                if i == cidade_idx and j < busca_idx:
                    continue
                
                save_checkpoint(i, j)
                
                termo = f"{busca} {cidade}"
                url = f"https://www.google.com/maps/search/{termo.replace(' ', '+')}"
                
                log_info(f"\n=== {termo} ===")
                
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    time.sleep(3)
                except:
                    continue
            
                try:
                    botao = page.locator('button:has-text("Pesquisar nesta Área")')
                    if botao.count() > 0:
                        botao.first.click()
                        time.sleep(2)
                except:
                    pass
                
                seen = set()
                
                # Scroll mais rápido
                for scroll in range(20):
                    time.sleep(1)
                    
                    cards = page.locator('.Nv2PK, div[role="article"]')
                    count = cards.count()
                    
                    if count == 0:
                        continue
                    
                    log_info(f"Scroll {scroll+1}: {count} cards")
                    
                    for k in range(count):
                        try:
                            card = cards.nth(k)
                            
                            link = card.locator('a').first
                            if link.count() == 0:
                                continue
                            href = link.get_attribute('href')
                            if not href or '/maps/' not in href:
                                continue
                            if not href.startswith('http'):
                                href = 'https://www.google.com' + href
                            
                            if href in seen or href in existing_links:
                                continue
                            seen.add(href)
                            
                            result = process_card_fast(page, card)
                            
                            if result:
                                dados = {
                                    'nome': result['nome'],
                                    'maps_link': result['maps_link'],
                                    'telefone': result['telefone'],
                                    'instagram': result['instagram'],
                                    'categoria': termo
                                }
                                
                                if salvar_lead(dados):
                                    total_salvo += 1
                                    existing_links.add(result['maps_link'])
                                    
                                    msg = f"[NOVO] {result['nome'][:30]}"
                                    if result['telefone']:
                                        msg += f" | [TEL]"
                                    if result['instagram']:
                                        msg += f" | [IG]"
                                    log_sucesso(msg)
                                    
                        except:
                            continue
                    
                    page.mouse.wheel(0, 1500)
                
                log_info(f"Busca '{busca}' em {cidade}: {len(seen)} processados")
            
            log_info(f"Total: {total_salvo} leads")
        
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        log_sucesso(f"\n=== FIM: {total_salvo} leads ===")

if __name__ == '__main__':
    run_scraper()
