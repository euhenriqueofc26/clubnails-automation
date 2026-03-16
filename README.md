# Club Nails Automation

Sistema de automação para extração de leads do Google Maps e envio via WhatsApp.

## Estrutura

- `database/leads.db` - Banco de dados SQLite com leads
- `scripts/` - Scripts Python para automação
- `config/settings.json` - Configurações do sistema
- `mensagens/mensagem_padrao.txt` - Modelo de mensagem WhatsApp
- `logs/execucao.log` - Log de execuções
- `n8n/workflow.json` - Workflow do n8n

## Configuração

1. Configure `config/settings.json` com suas credenciais
2. Customize `mensagens/mensagem_padrao.txt` conforme necessidade

## Uso

```bash
# Criar banco de dados
python scripts/criar_banco.py

# Executar scraping
python scripts/grid_maps_scraper.py

# Enviar mensagens
python scripts/enviar_whatsapp.py
```
