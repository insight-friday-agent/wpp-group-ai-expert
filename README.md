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
| `src/agent` | Artefatos que usam o vetor store (pgvector) com promps declarativos e reranking pelo Agno framework. |
| `docs/architecture.md` | Diagrama textual do fluxo e integrações planejadas. |

## Dados de exemplo
- `sample_data/messages_template.json`: mensagens sintéticas curtas para testes rápidos.
- Use `scripts/parse_whatsapp_export.py` para converter um export real (como o arquivo que você enviou) em JSON estruturado e alimentar a pipeline local.

## Próximos passos
- Integrar com a API oficial (ou não oficial) usando o collector que já está em `src/ingestion`.
- Levantar o vetor store em Postgres+pgvector e habilitar a busca híbrida (vetorial + LIKE) e o reranking via Agno.
- Configurar o modelo local com Ollama e documentar como rodar o Agno Agent para responder perguntas com o contexto do WhatsApp.
