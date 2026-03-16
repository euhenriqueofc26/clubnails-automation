import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def extrair_dados_maps(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    leads = []
    for item in dados.get('results', []):
        lead = {
            'nome': item.get('name', ''),
            'telefone': item.get('formatted_phone_number', ''),
            'endereco': item.get('formatted_address', ''),
            'categoria': item.get('types', [''])[0],
            'avaliacao': item.get('rating', 0),
            'fonte': 'google_maps'
        }
        leads.append(lead)
    
    return leads

if __name__ == '__main__':
    print("Função de extração de dados do Google Maps")
