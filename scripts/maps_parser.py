from utils.logger import log_info, log_warning

def parse_card(card):
    try:
        dados = {
            'nome': '',
            'endereco': '',
            'avaliacao': 0,
            'categoria': '',
            'telefone': '',
            'maps_link': ''
        }
        
        try:
            dados['nome'] = card.locator('.qBF1Pd').first.inner_text()
        except:
            try:
                dados['nome'] = card.locator('span').first.inner_text()
            except:
                return None
        
        try:
            endereco_elem = card.locator('.W4Efsd span')
            if endereco_elem.count() > 0:
                dados['endereco'] = endereco_elem.first.inner_text()
        except:
            pass
        
        try:
            rating_elem = card.locator('.MW4etd')
            if rating_elem.count() > 0:
                rating_text = rating_elem.first.inner_text()
                dados['avaliacao'] = float(rating_text.replace(',', '.'))
        except:
            pass
        
        try:
            categoria_elem = card.locator('.W4Efsd span:nth-child(2)')
            if categoria_elem.count() > 0:
                dados['categoria'] = categoria_elem.first.inner_text()
        except:
            pass
        
        try:
            telefone_elem = card.locator('span[data-phone-number]')
            if telefone_elem.count() > 0:
                dados['telefone'] = telefone_elem.first.get_attribute('data-phone-number')
        except:
            pass
        
        try:
            link_elem = card.locator('a').first
            if link_elem.count() > 0:
                href = link_elem.get_attribute('href')
                if href and ('maps.google' in href or 'google.com/maps' in href):
                    if not href.startswith('http'):
                        href = 'https://www.google.com' + href
                    dados['maps_link'] = href
        except:
            pass
        
        if dados['nome'] and dados['maps_link']:
            return dados
        
        return None
        
    except Exception as e:
        return None

def parse_todos_resultados(page):
    establishments = []
    seen_links = set()
    
    cards = page.locator('.Nv2PK')
    if cards.count() == 0:
        cards = page.locator('[data-result-index]')
    
    log_info(f"Parseando {cards.count()} cards...")
    
    for i in range(cards.count()):
        try:
            card = cards.nth(i)
            dados = parse_card(card)
            
            if dados and dados['maps_link'] and dados['maps_link'] not in seen_links:
                seen_links.add(dados['maps_link'])
                establishments.append(dados)
                
        except Exception as e:
            continue
    
    log_info(f"Parseados {len(establishments)} estabelecimentos válidos")
    return establishments
