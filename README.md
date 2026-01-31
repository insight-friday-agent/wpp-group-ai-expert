# WPP Group AI Expert

Pipeline para ingestão contínua de um grupo WhatsApp privado (via API não oficial) e criação de um agente RAG para responder perguntas sobre o contexto compartilhado.

## Objetivos imediatos
1. Capturar mensagens do grupo em tempo real ou polling com a API não oficial.
2. Normalizar e armazenar o conteúdo em um vetor store ou banco leve.
3. Operacionalizar um agente que responde perguntas baseadas nos dados recentes com RAG.

## Componentes principais
| Camada | Descrição |
| --- | --- |
| `src/ingestion` | Cliente e scheduler para ler a fila do WhatsApp e persistir no storage intermediário. |
| `src/pipeline` | Transformações, enriquecimentos (cleaning, chunking, embeddings) e roteamento para o agente. |
| `src/agent` | Artefatos que usam o vetor store (ou cache local) com prompts declarativos para responder perguntas em linguagem natural. |
| `docs/architecture.md` | Diagrama textual do fluxo e integrações planejadas. |

## Próximos passos
- Integrar com uma instância realmente autenticada da API (Twilio Authtoken, Chat API ou similar).
- Escolher e configurar o vetor store (ex: Weaviate, Milvus, Redis + embeddings).
- Definir o modelo RAG (Claude/Anthropic, OpenAI ou local) e o prompt template do agente.
