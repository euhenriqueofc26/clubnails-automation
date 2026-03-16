import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def gerar_mensagem(nome, template_path=None):
    if template_path is None:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'mensagens', 'mensagem_padrao.txt')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    mensagem = template.format(nome=nome)
    return mensagem

if __name__ == '__main__':
    print("Função de geração de mensagem")
