import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import export_to_csv, get_leads_count

def exportar_contatos(nome_arquivo='contatos.csv'):
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), nome_arquivo)
    
    print(f"Exportando contatos para: {caminho}")
    total = export_to_csv(caminho)
    print(f"Exportacao concluida! {total} contatos exportados.")

if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else 'contatos.csv'
    exportar_contatos(nome)
