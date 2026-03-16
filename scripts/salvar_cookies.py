import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def salvar_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 60)
        print("FAÇA LOGIN MANUAL NO GOOGLE:")
        print("1. Faça login com sua conta Google")
        print("2. Quando ver sua conta logada, volte aqui")
        print("3. O script vai salvar os cookies automaticamente")
        print("=" * 60)
        
        page.goto("https://accounts.google.com", wait_until="domcontentloaded")
        
        # Espera 60 segundos para login
        print("Aguarde 60 segundos para fazer login...")
        time.sleep(60)
        
        # Salva cookies
        cookies = context.cookies()
        
        cookies_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'cookies.json')
        with open(cookies_path, 'w') as f:
            json.dump(cookies, f)
        
        print(f"\nCookies salvas! ({len(cookies)} cookies)")
        print(f"Arquivo: {cookies_path}")
        
        browser.close()

if __name__ == '__main__':
    salvar_cookies()
