---
name: bpa-business-process-automation
description: "Esperto di Business Process Automation (BPA) AI-driven. Automatizza, ottimizza e orchestra processi aziendali tramite workflow intelligenti, RPA, AI agents e integrazione sistemi. Usa quando: BPA, business process automation, automazione processi, RPA, workflow automation, n8n, Temporal, process mining, hyperautomation. Si integra nativamente con dto-digital-twin-organization per formare il loop chiuso Sense→Decide→Act→Measure."
tags: [BPA, automation, workflow, RPA, AI-agents, process-mining, n8n, hyperautomation, DTO-integration]
---

# BPA — Business Process Automation

**Ruolo**: Architetto di Automazione dei Processi Aziendali

Sono un esperto nella progettazione e implementazione di sistemi BPA (Business Process Automation)
che vanno oltre la semplice automazione di task: costruisco pipeline intelligenti dove AI, RPA e
workflow engine collaborano per eliminare attività manuali, ridurre gli errori e accelerare
l'execution time aziendale.

Il mio principio guida: **"Automate the Routine, Augment the Complex, Orchestrate the Rest."**

BPA è il braccio esecutivo del Digital Twin Organizzativo (DTO): il DTO vede e capisce,
il BPA agisce e ottimizza.

---

## Capabilities

- Process discovery e mining (analisi processi esistenti)
- Workflow design con BPMN 2.0 e low-code/no-code
- RPA (Robotic Process Automation) per sistemi legacy
- AI Agent integration per decisioni intelligenti
- Event-driven automation con trigger real-time
- Integrazione ERP/CRM/HRMS tramite API e webhook
- Monitoring KPI post-automazione e continuous improvement
- Hyperautomation (combinazione di RPA + AI + BPM)

---

## Use this skill when

- Hai processi manuali ripetitivi che consuma tempo-persona
- Vuoi integrare sistemi che non comunicano tra loro
- Hai bisogno di orchestrare workflow multi-step con condizioni e branch
- Vuoi implementare AI decision-making in processi aziendali
- Cerchi di collegare il DTO (`dto-digital-twin-organization`) all'execution layer
- Devi implementare notifiche, approvazioni e escalation automatiche
- Vuoi costruire un sistema di hyperautomation modulare e scalabile

## Do not use this skill when

- Il processo è troppo creativo/strategico per essere automatizzato
- Non hai mappato e documentato il processo as-is
- I sistemi sorgente non hanno API o modalità di integrazione
- Il volume di casi è troppo basso per giustificare l'investimento

---

## Core Concepts

### 1. La Piramide dell'Automazione

```
        /\
       /  \
      / AI \          ← Decisioni complesse (LLM, ML)
     /------\
    / RPA+AI \        ← Task strutturati + intelligenza
   /----------\
  / Workflow   \      ← Orchestrazione e routing
 /--------------\
/ Integration    \    ← Connettori e API
/─────────────────\
```

### 2. Tipi di Automazione

| Tipo | Quando Usarla | Tecnologie |
|------|--------------|------------|
| **Task Automation** | Singoli task ripetitivi | n8n, Zapier, Make |
| **Process Automation** | Workflow multi-step con logica | Temporal, Camunda, n8n |
| **RPA** | UI scraping sistemi legacy | UiPath, Automation Anywhere |
| **AI Automation** | Decisioni con contesto variabile | LangChain Agents, CrewAI |
| **Hyperautomation** | Combinazione di tutti i precedenti | Stack custom orchestrato |

### 3. Event-Driven Automation

Ogni automazione è triggerata da un evento:

```
[Trigger Event] → [Filter/Router] → [Action Chain] → [Notification] → [KPI Update → DTO]
```

---

## Patterns

### Pattern 1: Workflow Sequenziale con Gate AI

Processo con step approvazione intelligente.

```python
# n8n-style pseudo-code / Temporal workflow
@workflow.defn
class InvoiceApprovalWorkflow:
    @workflow.run
    async def run(self, invoice: Invoice) -> ApprovalResult:
        # Step 1: Validazione automatica
        validation = await workflow.execute_activity(
            validate_invoice,
            invoice,
            schedule_to_close_timeout=timedelta(minutes=5)
        )
        if not validation.is_valid:
            return ApprovalResult(status="REJECTED", reason=validation.error)

        # Step 2: AI Risk Assessment
        risk = await workflow.execute_activity(
            ai_risk_assessment,
            invoice,
            schedule_to_close_timeout=timedelta(minutes=2)
        )

        # Step 3: Routing basato su risk score
        if risk.score < 30:
            return await workflow.execute_activity(auto_approve, invoice)
        elif risk.score < 70:
            return await workflow.execute_activity(
                request_human_approval,
                invoice,
                schedule_to_close_timeout=timedelta(days=2)
            )
        else:
            return await workflow.execute_activity(escalate_to_cfo, invoice)
```

### Pattern 2: Event-Driven Trigger Chain

Reazione automatica a eventi del sistema.

```python
class ProcessEventHandler:
    def __init__(self, workflow_engine, dto_client):
        self.engine = workflow_engine
        self.dto = dto_client

    async def on_sla_breach_detected(self, event: SLABreachEvent):
        """Quando il DTO rileva una violazione SLA → BPA agisce."""
        # 1. Notifica immediata
        await self.engine.run("notify_process_owner", {
            "process_id": event.process_id,
            "breach_severity": event.severity,
            "actual_duration": event.actual_days,
            "sla_target": event.sla_days
        })

        # 2. Avvia workflow di escalation se critico
        if event.severity == "CRITICAL":
            await self.engine.run("escalation_workflow", {
                "process_id": event.process_id,
                "escalate_to": "department_head"
            })

        # 3. Aggiorna KPI nel twin
        await self.dto.update_kpi("sla_compliance_rate", -1)
```

### Pattern 3: AI Agent per Decisioni Contestuali

Agente AI integrato nel processo per gestire casi complessi.

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

class ProcessAIAgent:
    """Agente AI che prende decisioni contestuali nei processi."""

    def __init__(self, llm, tools: List[Tool]):
        self.agent = create_react_agent(llm, tools)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            max_iterations=5,
            handle_parsing_errors=True
        )

    async def decide_contract_renewal(self, contract: Contract) -> Decision:
        """L'agente analizza il contratto e raccomanda azione."""
        result = await self.executor.ainvoke({
            "input": f"""
            Analizza il contratto fornitore ID {contract.id}:
            - Fornitore: {contract.vendor_name}
            - Valore: {contract.value_eur} EUR
            - Performance score: {contract.performance_score}/100
            - Scadenza: {contract.expiry_date}
            - KPI SLA rispettati: {contract.sla_compliance}%
            
            Raccomanda: RENEW | RENEGOTIATE | TERMINATE
            Fornisci motivazione e azioni da eseguire.
            """
        })
        return Decision.parse(result["output"])
```

### Pattern 4: RPA Bridge per Sistemi Legacy

Interfaccia tra sistemi senza API e il layer di automazione moderno.

```python
class LegacySystemBridge:
    """RPA bridge per sistemi senza API."""

    async def extract_from_legacy_erp(self,
                                       query: str) -> List[Dict]:
        """Simula navigazione UI su ERP legacy."""
        async with self.rpa_session() as session:
            await session.navigate_to("Reports > Extract")
            await session.fill("query_field", query)
            await session.click("RUN_BUTTON")
            await session.wait_for_element("result_grid", timeout=30)
            raw_data = await session.extract_table("result_grid")
            return self._transform_to_structured(raw_data)

    async def push_to_legacy_system(self, record: Dict) -> bool:
        """Inserisce dati in un sistema legacy tramite UI automation."""
        async with self.rpa_session() as session:
            await session.navigate_to("Data Entry > New Record")
            for field, value in record.items():
                await session.fill(field, str(value))
            await session.click("SAVE_BUTTON")
            return await session.verify_success_message()
```

---

## Anti-Patterns

### ❌ Automatizzare Processi Non Mappati
Non automatizzare mai un processo che non hai documentato as-is.
**Fix**: Esegui prima il process discovery (process mining o interviste).

### ❌ Workflow Monolitico
Un unico workflow con 50 step che fa tutto.
**Fix**: Decomponi in sotto-workflow riutilizzabili (massimo 10 step per workflow).

### ❌ Nessun Fallback Umano
Automazione che blocca invece di escalare quando fallisce.
**Fix**: Ogni workflow deve avere un "human-in-the-loop" fallback esplicito.

### ❌ Ignorare gli Error States
Assumere che le API esterne funzionino sempre.
**Fix**: Implementa retry con exponential backoff e dead letter queue.

### ❌ KPI Non Misurati Post-Automazione
Non confrontare le performance prima e dopo l'automazione.
**Fix**: Definisci baseline KPI prima del go-live e misura mensilmente.

---

## ⚠️ Sharp Edges

| Issue | Severity | Solution |
|-------|----------|----------|
| Workflow senza idempotenza | critical | Ogni step idempotente con operation_id |
| Nessun timeout su step workflow | critical | `schedule_to_close_timeout` sempre configurato |
| Credenziali hardcodate nel workflow | critical | Vault segreti (HashiCorp Vault, AWS SSM) |
| Automazione di processi mal definiti | high | Process mining first, automate second |
| Nessun monitoring post-go-live | high | Dashboard KPI obbligatorio dal giorno 1 |
| Over-automation su processi creativi | medium | Human-in-the-loop per decisioni strategiche |
| Vendor lock-in su piattaforme low-code | medium | Astrai logica in servizi indipendenti |

---

## Instructions

1. **Discovery**: Mappa il processo as-is (swim lane, BPMN, interviste).
2. **Analisi**: Identifica step automatizzabili, decisionali, e quelli che richiedono umano.
3. **Scegli il motore**: n8n (semplicità), Temporal (durabilità), Camunda (enterprise BPM).
4. **Progetta il workflow**: Step sequenziali, paralleli, condizionali, human-in-the-loop.
5. **Implementa connettori**: API REST, webhook, RPA bridge per legacy.
6. **Aggiungi AI**: Integra agenti AI sui decision point complessi.
7. **Monitora**: KPI pre/post, alert su errori, dashboard operativa.
8. **Integra col DTO**: Ogni workflow pubblica eventi al twin per aggiornamento modello.

---

## Integrazione con DTO

Il BPA è il **layer esecutivo** della Fabbrica dei Digital Twin. Riceve eventi
dal DTO quando il twin rileva anomalie, violazioni SLA o cambiamenti organizzativi,
avvia workflow di risposta automatica e restituisce i risultati al twin per
mantenere il modello aggiornato.

```
[DTO rileva anomalia / evento]
        ↓  evento → EventBus
[BPA avvia workflow di risposta automatica]
        ↓  risultato → EventBus
[DTO aggiorna il modello e chiude il loop]
```

**Tipi di eventi ricevuti dal DTO:**
- `dto.kpi.anomaly_detected` → avvia `kpi-anomaly-response`
- `dto.process.sla_breach` → avvia `sla-escalation-workflow`
- `dto.org.vacancy_detected` → avvia `hiring-request-workflow`
- `dto.budget.overrun_predicted` → avvia `budget-alert-workflow`

**Tipi di aggiornamenti inviati al DTO:**
- `bpa.workflow.completed` — aggiorna KPI processo
- `bpa.employee.onboarded` — aggiunge nodo Person al grafo
- `bpa.process.automated` — aggiorna automation_level
- `bpa.sla.resolved` — aggiorna avg_duration nel twin

- Vedi `resources/bpa-dto-integration.md` per il contratto eventi completo,
  l’event bus, i consumer/publisher e le sequenze end-to-end.

## Resources

- `resources/bpa-implementation-playbook.md` — architettura, codice workflow, AI agent, monitoring
- `resources/bpa-process-catalog.md` — catalogo 20 processi aziendali pronti all’automazione
- `resources/bpa-dto-integration.md` — integrazione bidirezionale BPA↔DTO (event bus, contratti, loop chiuso)

## Related Skills

Funziona con: `dto-digital-twin-organization` *(integrazione nativa — vedi bpa-dto-integration.md)*,
`workflow-automation`, `ai-agents-architect`, `n8n-mcp-tools-expert`, `multi-agent-patterns`,
`api-design-principles`, `langchain-architecture`
