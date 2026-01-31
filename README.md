# WPP Group AI Expert

Pipeline para ingestão contínua de um grupo WhatsApp privado (via API não oficial) e criação de um agente RAG para responder perguntas sobre o contexto compartilhado.

## Objetivos imediatos
1. Capturar mensagens do grupo em tempo real ou via polling com a API não oficial.
2. Normalizar e armazenar o conteúdo em um vetor store (pgvector) e um banco leve.
3. Operacionalizar um agente que responde perguntas baseadas nos dados recentes com RAG híbrido (vetorial + simbólico) e reranking.

## Componentes principais
| Camada | Descrição |
| --- | --- |
| `src/ingestion` | Cliente e scheduler para ler a fila do WhatsApp, persistir no storage intermediário e gerar ingestão contínua. |
| `src/pipeline` | Transformações, chunking, embeddings e roteamento híbrido para o vetor store e o agente. |
| `src/agent` | Artefatos que usam o vetor store (pgvector) com prompts declarativos e reranking pelo Agno framework. |
| `docs/architecture.md` | Diagrama textual do fluxo e integrações planejadas. |

## Dados de exemplo
- `sample_data/messages_template.json`: mensagens sintéticas curtas para testes rápidos e para cobrir eventos/cultos.
- `sample_data/quenotebook.json` (gerado com `scripts/fetch_quenotebook.py`): trechos selecionados do site `quenotebookcomprar.com.br`.
- `sample_data/whatsapp_export.json`: JSON produzido por `scripts/parse_whatsapp_export.py` a partir do export real que você compartilhou.

## Scripts principais
| Comando | O que faz |
| --- | --- |
| `python scripts/fetch_quenotebook.py` | Baixa os principais blocos de texto do site e salva em `sample_data/quenotebook.json` para alimentar a ingestão. |
| `python scripts/parse_whatsapp_export.py PATH --output sample_data/whatsapp_export.json` | Converte o export de WhatsApp em JSON estruturado para testes locais. |
| `python scripts/seed_pgvector.py` | Conecta ao Postgres (`PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`), cria as tabelas e indexa todos os samples no pgvector. |
| `python scripts/judge_agent.py` | Executa queries de validação, roda o agente e julga as respostas com base em palavras-chave essenciais e citações. |
| `bash scripts/auto_judge.sh` | Loop que roda `judge_agent.py`, grava logs em `logs/judge.log` e repete a cada 2 minutos até passar. |

## Próximos passos
- Integrar com a API oficial (ou não oficial) usando o collector que já está em `src/ingestion`.
- Levantar o vetor store em Postgres+pgvector e habilitar a busca híbrida (vetorial + LIKE) e o reranking via Agno.
- Configurar o modelo local com Ollama e documentar como rodar o Agno Agent para responder perguntas com o contexto do WhatsApp.
