# Agno + Ollama local stack para o WPP Group AI Expert

## Objetivo
Integraremos o pipeline híbrido (pgvector + reranking) com um agente Agno que chama um modelo local via Ollama. Assim testamos o RAG completo em um ambiente off‑line antes de ligar a API oficial ou os serviços em nuvem.

## Componentes
1. **Context retrieval** (`src/retrieval/hybrid.py`) → rodar busca vetorial + heurística textual em pgvector.
2. **Agno prompt template** (abstraído no script de execução) → descreve o papel do agente, critérios de qualidade, referências e citações.
3. **Modelo local** → `ollama` (ex: `ollama run llama3` ou qualquer modelo instalado). A ênfase é em manter tudo local para testes rápidos.

## Setup mínimo
1. **Instale Ollama** (script com `sudo`):
   ```bash
   curl -s https://ollama.com/install.sh | sudo sh
   ollama pull llama3
   ```
2. **Defina o modelo local** (env var `OLLAMA_MODEL`, padrão `llama3`).
3. **Execute o script de prompt**:
   ```bash
   cd ~/git/wpp-group-ai-expert
   .venv/bin/python scripts/run_agno_agent.py "Qual é a última agenda?"
   ```

O script combina o texto recuperado via `HybridRetriever` com um prompt Agno, chama `ollama run $OLLAMA_MODEL --prompt "<prompt>"` e renderiza a resposta com citações.

## Integração com o Agno framework (planejamento)
- O prompt segue a estrutura `## Your Role`, `## Input`, `## Process`, `## Output` documentada na skill `agent-development`.
- O reranking de recência serve como `blocking check` (ex.: só responde se houver contextos de 24h).
- Em um próximo passo podemos mover o prompt para um arquivo `.claude/agents/whatsapp-insights.md` e deixar o serviço Agno assumir (execução via `agno run` ou `claude`). No momento rodamos `ollama` diretamente, mas a estrutura de prompt já está pronta para migrar.
