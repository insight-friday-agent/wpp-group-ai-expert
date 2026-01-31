# Arquitetura proposta: WPP Group AI Expert

1. **Ingestão contínua**
   - Agente de coleta (`UnofficialWhatsAppClient`) que mantém sessão com a API não oficial e coleta eventos de mensagem.
   - Persistência imediata em um `MessageStore` local (SQLite + textos brutos) com metadados (timestamp, autor, tipo).
   - Retry/backoff e confirmação de leitura para garantir que não perca mensagens quando o client falhar.

2. **Pipeline de normalização**
   - Transformador (`ConversationProcessor`) para dividir conversas em chunks curtos (200 tokens), detectar temas e anexar contexto.
   - Embelezamento: gerar embeddings via `OpenAIEmbeddings` ou outro provedor (abstraído em `EmbeddingsFactory`).
   - Armazenamento em vetor store leve como `Chroma`/`RedisVector`, com namespaces (`group_id`, `message_id`).

3. **Agente RAG interativo**
   - Componente `WhatsAppInsightsAgent` que consulta o vetor store com a pergunta e usa prompt declarativo:
     ```
     ## Your Role
     RAG specialist for the "comunidade" WhatsApp group.
     Use context from the vector store when answering.
     ## Blocking Check
     - Ensure embeddings exist for the last 24h of messages.
     ## Input
     - question: user query
     ## Process
     1. Retrieve top 5 chunks.
     2. Summarize if needed, then produce answer referencing timestamps.
     3. Flag if data is outdated.
     ## Output
     - answer: string (use inline citations)
     ```
   - Resposta devolvida via API (FastAPI ou webhook) para o client que fizer a pergunta.

4. **Orquestração**
   - Cron scheduler (ou `prefect`) para manter a ingestão ativa e disparar re-indexações.
   - Webhook HTTP (ou Socket) para receber query do usuário/cliente e retornar com o agente.

5. **Observabilidade**
   - Logs estruturados, métricas de ingestão (mensagens/hora), latência de respostas do agente.
   - Endpoint `/status` (FastAPI) para verificar quantos chunks estão indexados no Postgres + pgvector.

6. **Busca híbrida + reranking**
   - `HybridRetriever` combina buscas vetoriais (pgvector) com match token/termos para garantir recall simbólico.
   - `SimpleReranker` aplica heurísticas de recência e similaridade textual antes de montar o prompt para o Agno Agent.

## Próximas ações técnicas
- Materializar o client e o scheduler de ingestion no `src/ingestion`.
- Criar testes unitários (ex: fixtures sample_data) que simulam novas mensagens e confirmam escrita no storage.
- Montar o prompt template e a interface HTTP para o agente (FastAPI + background task).
- Padronizar as validações com `scripts/judge_agent.py`, garantindo que cada query experimental seja julgada automaticamente.
