# Istruzioni per l'Agente

## Gestione Skills Autonoma

Durante lo sviluppo, l'agente e' AUTORIZZATO a scaricare nuove skills in autonomia senza chiedere permesso all'utente.

### Repository Skills
- **URL**: https://github.com/sickn33/antigravity-awesome-skills
- **Path locale**: `.agent/skills/`

### Procedura Autonoma
1. Identificare la skill necessaria dal catalogo (CATALOG.md nel repo)
2. Verificare se gia' presente in `.agent/skills/`
3. Se assente, eseguire `git pull` per aggiornare il repo
4. Utilizzare la skill immediatamente

### Catalogo Skills Disponibili (631+)
- **Architecture** (52): architecture, c4-context, senior-architect
- **Business** (35): copywriting, pricing-strategy, seo-audit  
- **Data & AI** (81): rag-engineer, prompt-engineer, langgraph
- **Development** (72): typescript-expert, python-patterns, react-patterns
- **General** (95): brainstorming, doc-coauthoring, writing-plans
- **Infrastructure** (72): docker-expert, aws-serverless, vercel-deployment
- **Security** (107): api-security-best-practices, sql-injection-testing
- **Testing** (21): test-driven-development, testing-patterns, test-fixing
- **Workflow** (17): workflow-automation, inngest, trigger-dev

### MCP Servers Disponibili
- **URL**: https://github.com/modelcontextprotocol/servers
- **Path locale**: `.agent/mcp/`
- Installati: filesystem, git, memory, fetch, sequentialthinking

---

## Metodologia Sacchi
- Safety-first: Mai lavorare su `main`
- Little-often: Commit atomici dopo ogni test passato
- Double-check: Test suite prima di ogni merge
