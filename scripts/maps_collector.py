import random
from playwright.sync_api import Page
from utils.logger import log_info, log_erro, log_warning
from utils.random_delay import random_delay, random_delay_between_actions

ZOOM_LEVEL = 13

def buscar_pesquisar_na_area(page):
    try:
        page.wait_for_timeout(2000)
        
        selectors = [
            'button:has-text("Pesquisar nesta área")',
            'button:has-text("Search this area")',
            'button[aria-label*="Pesquisar"]',
            'div[class*="searchbox"] button'
        ]
        
        for selector in selectors:
            buttons = page.locator(selector)
            if buttons.count() > 0:
                for i in range(min(buttons.count(), 3)):
                    btn = buttons.nth(i)
                    try:
                        text = btn.inner_text()
                        if text and ('área' in text.lower() or 'area' in text.lower() or 'Pesquisar' in text):
                            btn.click()
                            log_info(f"Clicou em '{text}'")
                            return True
                    except:
                        continue
        
        log_warning("Botão 'Pesquisar nesta área' não encontrado")
        return False
    except Exception as e:
        log_warning(f"Erro ao buscar botão: {e}")
        return False

def esperar_resultados_atualizarem(page, timeout=10000):
    page.wait_for_timeout(timeout)
    
    cards = page.locator('.Nv2PK')
    count = cards.count()
    
    for _ in range(6):
        page.wait_for_timeout(1500)
        new_count = page.locator('.Nv2PK').count()
        if new_count != count:
            log_info(f"Resultados atualizados: {count} -> {new_count}")
            page.wait_for_timeout(2000)
            return True
        count = new_count
    
    log_warning("Resultados não atualizaram")
    return False

def pan_map(page, dx, dy):
    try:
        viewport = page.viewport_size
        center_x = viewport['width'] // 2
        center_y = viewport['height'] // 2
        
        page.mouse.move(center_x, center_y)
        page.mouse.down()
        page.mouse.move(center_x + dx, center_y + dy, steps=10)
        page.mouse.up()
        
        random_delay_between_actions()
        return True
    except Exception as e:
        log_warning(f"Erro ao mover mapa: {e}")
        return False

def buscar_nesta_area_após_pan(page):
    page.wait_for_timeout(2000)
    
    button_found = False
    
    try:
        btn = page.locator('button:has-text("Pesquisar nesta área"), button:has-text("Search this area")')
        if btn.count() > 0:
            btn.first.click()
            button_found = True
            log_info("Clicou em 'Pesquisar nesta área'")
    except:
        pass
    
    if not button_found:
        try:
            page.keyboard.press('Enter')
            log_info("Pressionou Enter para buscar")
            button_found = True
        except:
            pass
    
    if button_found:
        esperar_resultados_atualizarem(page, timeout=8000)
    
    return button_found

def executar_busca_inicial(page, termo_busca):
    try:
        search_box = page.locator('input#searchboxinput, input[name="q"], input.searchboxinput')
        
        if search_box.count() == 0:
            log_warning("Campo de busca não encontrado")
            return False
        
        search_box.first.click()
        random_delay(0.5, 1.5)
        
        search_box.first.fill(termo_busca)
        random_delay(0.5, 1)
        
        page.keyboard.press('Enter')
        random_delay(4, 7)
        
        return True
    except Exception as e:
        log_erro(f"Erro ao executar busca: {e}")
        return False

def aceitar_cookies(page):
    try:
        selectors = [
            'button:has-text("Aceitar")',
            'button:has-text("Accept")', 
            'button[aria-label*="Aceitar"]',
            'button.VfPpkd-LgbsSe'
        ]
        
        for selector in selectors:
            buttons = page.locator(selector)
            if buttons.count() > 0:
                buttons.first.click()
                random_delay(1, 2)
                return True
        return False
    except:
        return False

def inicializar_browser(headless=False):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            log_info("Browser inicializado com sucesso")
            return browser, context, page
            
    except Exception as e:
        log_erro(f"Erro ao inicializar browser: {e}")
        raise
