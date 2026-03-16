import random
from utils.logger import log_info, log_warning
from utils.random_delay import random_delay

def scroll_ate_carregar_todos(page, min_results=100, max_scrolls=40):
    log_info(f"Iniciando scroll para coletar pelo menos {min_results} resultados...")
    
    establishments = []
    seen_links = set()
    
    last_count = 0
    no_change_rounds = 0
    
    for scroll_round in range(max_scrolls):
        page.wait_for_timeout(2500)
        
        page.evaluate('''
            const container = document.querySelector('.ZKC9wd') || document.querySelector('.YfNQwc');
            if (container) {
                container.scrollBy(0, 1500);
            }
        ''')
        
        page.wait_for_timeout(1000)
        
        cards = page.locator('.Nv2PK')
        if cards.count() == 0:
            cards = page.locator('[data-result-index]')
        if cards.count() == 0:
            cards = page.locator('div[class*="Nv2PK"]')
        
        count = cards.count()
        
        if count > last_count:
            no_change_rounds = 0
        else:
            no_change_rounds += 1
        
        if no_change_rounds >= 5:
            log_warning(f"Sem novos resultados por 5 rodadas. Parando.")
            break
        
        last_count = count
        
        for i in range(count):
            try:
                card = cards.nth(i)
                
                nome = ""
                try:
                    nome = card.locator('.qBF1Pd').first.inner_text()
                except:
                    try:
                        nome = card.locator('span').first.inner_text()
                    except:
                        continue
                
                link = ""
                link_elem = card.locator('a').first
                if link_elem.count() > 0:
                    href = link_elem.get_attribute('href')
                    if href and ('maps.google' in href or 'google.com/maps' in href):
                        if not href.startswith('http'):
                            href = 'https://www.google.com' + href
                        link = href
                
                if nome and link and link not in seen_links:
                    seen_links.add(link)
                    establishments.append({'nome': nome, 'link': link})
                    
            except Exception as e:
                continue
        
        log_info(f"Rodada {scroll_round + 1}: {len(establishments)} establishments únicos")
        
        if len(establishments) >= min_results:
            log_info(f"Objetivo alcançado: {len(establishments)} resultados")
            break
        
        random_delay(0.3, 0.8)
    
    log_info(f"Total coletado no scroll: {len(establishments)}")
    return establishments

def verificar_mais_resultados(page):
    try:
        more_button = page.locator('button:has-text("Mais resultados"), button:has-text("mais resultados")')
        if more_button.count() > 0:
            more_button.first.click()
            return True
    except:
        pass
    return False
