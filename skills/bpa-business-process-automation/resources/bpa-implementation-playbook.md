# BPA — Business Process Automation
## Implementation Playbook

---

## 1. Architettura di Riferimento

### Vista BPA Completa

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TRIGGER LAYER                               │
│   WebHook · Schedule (CRON) · Event Bus · Manual · API Call        │
├─────────────────────────────────────────────────────────────────────┤
│                      ORCHESTRATION LAYER                            │
│        Workflow Engine (Temporal / n8n) · State Machine            │
├──────────────┬──────────────────────┬──────────────────────────────┤
│  INTEGRATION │    AI DECISION       │    HUMAN-IN-THE-LOOP         │
│  LAYER       │    LAYER             │    LAYER                     │
│  ERP · CRM   │  LLM Agent           │  Approval Inbox              │
│  HRMS · API  │  ML Classifier       │  Task Assignment             │
│  RPA Bridge  │  Rule Engine         │  Escalation Chain            │
├──────────────┴──────────────────────┴──────────────────────────────┤
│                      MONITORING LAYER                               │
│    KPI Dashboard · Alert System · Audit Log · DTO Sync             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stack Tecnologico

| Componente | Opzione Standard | Opzione Enterprise |
|------------|-----------------|-------------------|
| Workflow Engine | n8n self-hosted | Temporal.io + Camunda |
| AI Decision | LangChain + OpenRouter | Azure AI + OpenAI |
| RPA | Playwright/Puppeteer | UiPath, Automation Anywhere |
| Event Bus | Redis Streams | Apache Kafka |
| Integration | REST + Webhooks | MuleSoft, Dell Boomi |
| Monitoring | Grafana + Prometheus | Datadog, New Relic |
| Human Tasks | Custom Form App | Camunda Tasklist |
| Secrets | .env + dotenv | HashiCorp Vault |

---

## 3. Struttura Progetto BPA

```
bpa-project/
├── workflows/                    # Definizioni workflow
│   ├── invoice-approval/
│   │   ├── workflow.py           # Temporal workflow def
│   │   ├── activities.py         # Step atomici
│   │   └── schema.py             # Input/output types
│   ├── onboarding-employee/
│   └── supplier-renewal/
├── agents/                       # AI Agents
│   ├── risk_assessor.py
│   ├── contract_analyst.py
│   └── document_extractor.py
├── connectors/                   # Integrazioni esterne
│   ├── erp_connector.py
│   ├── crm_connector.py
│   ├── hrms_connector.py
│   └── legacy_rpa_bridge.py
├── rules/                        # Business rules (separato da codice)
│   ├── approval_thresholds.yaml
│   └── escalation_matrix.yaml
├── monitoring/
│   ├── kpi_tracker.py
│   └── dto_publisher.py          # Pubblica KPI al Digital Twin
├── api/
│   ├── main.py                   # FastAPI endpoint
│   └── schemas.py
├── tests/
└── config/
    ├── settings.yaml
    └── secrets.yaml.example
```

---

## 4. Implementazione Workflow Engine (Temporal)

### 4.1 Workflow Base con Error Handling

```python
import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
from dataclasses import dataclass
from typing import Optional

# ─── DATA MODELS ───────────────────────────────────────────────
@dataclass
class WorkflowInput:
    process_id: str
    entity_id: str
    payload: dict
    initiated_by: str

@dataclass
class WorkflowResult:
    status: str          # COMPLETED | FAILED | ESCALATED | PENDING_HUMAN
    output: dict
    execution_time_sec: float
    error: Optional[str] = None

# ─── ACTIVITIES (step atomici, idempotenti) ─────────────────────

@activity.defn
async def validate_input(data: dict) -> dict:
    """Valida input. DEVE essere idempotente."""
    required_fields = ["entity_id", "amount", "requester_id"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return {"is_valid": True, "cleaned_data": data}

@activity.defn
async def call_external_api(endpoint: str, payload: dict) -> dict:
    """Chiama API esterna con retry automatico."""
    import httpx
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(endpoint, json=payload)
        resp.raise_for_status()
        return resp.json()

@activity.defn
async def send_notification(recipient: str, message: str,
                             channel: str = "email") -> bool:
    """Invia notifica tramite canale specificato."""
    # Implementa: email, Slack, Teams, SMS
    connector = NotificationConnector(channel=channel)
    return await connector.send(recipient=recipient, body=message)

@activity.defn
async def request_human_approval(task_data: dict) -> dict:
    """Crea task umano e attende approvazione (async)."""
    task_id = await HumanTaskManager().create_task(
        title=task_data["title"],
        assignee=task_data["assignee"],
        data=task_data["payload"],
        deadline_hours=task_data.get("deadline_hours", 48)
    )
    # Il workflow si mette in sleep, non consuma CPU
    # L'approvazione sblocca il workflow via signal
    return {"task_id": task_id, "status": "PENDING"}

# ─── WORKFLOW ORCHESTRATOR ──────────────────────────────────────

@workflow.defn
class InvoiceApprovalWorkflow:
    """
    Processo: Approvazione Fattura Fornitore
    Trigger: Ricezione fattura da EDI/email
    Steps: Validate → AI Risk → Route → Approve/Escalate → Post
    """

    @workflow.run
    async def run(self, input: WorkflowInput) -> WorkflowResult:
        import time
        start = time.time()

        try:
            # ── Step 1: Validazione ────────────────────────────
            validation = await workflow.execute_activity(
                validate_input,
                input.payload,
                schedule_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            # ── Step 2: Arricchimento dati fornitore ───────────
            vendor_data = await workflow.execute_activity(
                call_external_api,
                f"{settings.erp_url}/vendors/{input.payload['vendor_id']}",
                {},
                schedule_to_close_timeout=timedelta(minutes=2)
            )

            # ── Step 3: AI Risk Assessment ────────────────────
            risk = await workflow.execute_activity(
                ai_risk_assessment,
                {**input.payload, "vendor": vendor_data},
                schedule_to_close_timeout=timedelta(minutes=3)
            )

            # ── Step 4: Routing Decision ──────────────────────
            if risk["score"] < 30 and input.payload["amount"] < 10_000:
                # AUTO-APPROVE
                result = await workflow.execute_activity(
                    auto_approve_invoice,
                    input.payload,
                    schedule_to_close_timeout=timedelta(minutes=5)
                )
                status = "COMPLETED"

            elif risk["score"] < 70:
                # HUMAN APPROVAL
                approver = self._get_approver(input.payload["amount"])
                await workflow.execute_activity(
                    send_notification,
                    approver,
                    f"Approvazione richiesta: fattura {input.entity_id}",
                    schedule_to_close_timeout=timedelta(minutes=1)
                )
                approval = await workflow.execute_activity(
                    request_human_approval,
                    {
                        "title": f"Approva fattura {input.entity_id}",
                        "assignee": approver,
                        "payload": input.payload,
                        "deadline_hours": 48
                    },
                    schedule_to_close_timeout=timedelta(days=3)
                )
                result = approval
                status = "COMPLETED" if approval["approved"] else "REJECTED"

            else:
                # ESCALATION
                await workflow.execute_activity(
                    escalate_to_management,
                    {**input.payload, "risk_score": risk["score"]},
                    schedule_to_close_timeout=timedelta(hours=1)
                )
                result = {"escalated": True, "risk": risk}
                status = "ESCALATED"

            return WorkflowResult(
                status=status,
                output=result,
                execution_time_sec=time.time() - start
            )

        except Exception as e:
            # Notifica errore + log nel DTO
            await workflow.execute_activity(
                send_notification,
                settings.ops_email,
                f"Workflow FAILED: {input.process_id} — {str(e)}"
            )
            return WorkflowResult(
                status="FAILED",
                output={},
                execution_time_sec=time.time() - start,
                error=str(e)
            )

    def _get_approver(self, amount: float) -> str:
        thresholds = ApprovalThresholds.load()
        for tier in thresholds.tiers:
            if amount <= tier.max_amount:
                return tier.approver_role
        return thresholds.default_escalation
```

---

## 5. AI Agent per Decisioni Contestuali

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import json

# ─── TOOLS DELL'AGENTE ─────────────────────────────────────────

def get_vendor_history(vendor_id: str) -> str:
    """Tool: storico transazioni fornitore."""
    history = ERPConnector().get_vendor_history(vendor_id, months=12)
    return json.dumps({
        "total_invoices": len(history),
        "avg_amount": sum(h["amount"] for h in history) / len(history),
        "late_payments": sum(1 for h in history if h["days_late"] > 5),
        "sla_compliance": sum(h["on_time"] for h in history) / len(history)
    })

def check_budget_availability(department: str, amount: float) -> str:
    """Tool: verifica budget disponibile."""
    budget = ERPConnector().get_budget(department)
    available = budget["allocated"] - budget["spent"]
    return json.dumps({
        "available_budget": available,
        "can_approve": available >= amount,
        "utilization_pct": (budget["spent"] / budget["allocated"]) * 100
    })

def get_compliance_rules(document_type: str) -> str:
    """Tool: regole compliance per tipo documento."""
    rules = ComplianceEngine().get_rules(document_type)
    return json.dumps(rules)

# ─── AGENTE CONFIGURATO ────────────────────────────────────────

class InvoiceRiskAgent:
    """Agente AI per valutazione rischio fattura."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.tools = [
            Tool(name="get_vendor_history",
                 func=get_vendor_history,
                 description="Ottieni storico transazioni fornitore. Input: vendor_id (string)"),
            Tool(name="check_budget_availability",
                 func=check_budget_availability,
                 description="Verifica disponibilità budget. Input: department, amount"),
            Tool(name="get_compliance_rules",
                 func=get_compliance_rules,
                 description="Regole compliance per tipo documento. Input: document_type")
        ]
        self.agent = create_react_agent(self.llm, self.tools, RISK_ASSESSMENT_PROMPT)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            max_iterations=6,
            handle_parsing_errors=True,
            verbose=True
        )

    async def assess_risk(self, invoice: dict) -> dict:
        result = await self.executor.ainvoke({
            "input": f"""
            Valuta il rischio di questa fattura fornitore e fornisci un risk score (0-100).
            
            Fattura:
            - ID: {invoice['id']}
            - Fornitore ID: {invoice['vendor_id']}
            - Importo: {invoice['amount']} EUR
            - Dipartimento: {invoice['department']}
            - Tipo: {invoice['document_type']}
            
            Usa i tool disponibili per verificare:
            1. Storico del fornitore
            2. Disponibilità budget
            3. Compliance rules
            
            Output OBBLIGATORIO in JSON:
            {{"score": <0-100>, "reasoning": "<spiegazione>", "flags": [<lista rischi>], "recommendation": "APPROVE|REVIEW|REJECT"}}
            """
        })
        return json.loads(result["output"])

RISK_ASSESSMENT_PROMPT = """Sei un analista finanziario esperto in valutazione rischio.
Usa i tool forniti per raccogliere informazioni e fornisce sempre una valutazione strutturata.
{tools}
{agent_scratchpad}
"""
```

---

## 6. Monitoring & DTO Integration

```python
class BPAMonitor:
    """Monitoring KPI automazione e sync con il Digital Twin."""

    def __init__(self, dto_client: DTOClient, metrics_store: MetricsStore):
        self.dto = dto_client
        self.metrics = metrics_store

    async def track_workflow_completion(self,
                                         workflow_id: str,
                                         result: WorkflowResult):
        """Traccia ogni completamento workflow e aggiorna DTO."""

        # 1. Salva metriche locali
        await self.metrics.record({
            "workflow_id": workflow_id,
            "status": result.status,
            "execution_time": result.execution_time_sec,
            "timestamp": datetime.utcnow()
        })

        # 2. Calcola KPI aggregati (rolling 24h)
        stats = await self.metrics.get_stats(workflow_id, hours=24)

        # 3. Pubblica al Digital Twin Organizzativo
        await self.dto.update_kpi(f"bpa.{workflow_id}.success_rate",
                                   stats["success_rate"])
        await self.dto.update_kpi(f"bpa.{workflow_id}.avg_time_sec",
                                   stats["avg_execution_time"])
        await self.dto.update_kpi(f"bpa.{workflow_id}.volume_24h",
                                   stats["total_executions"])

        # 4. Alert se KPI fuori soglia
        if stats["success_rate"] < 0.95:
            await self.dto.publish_event("bpa.kpi.alert", {
                "workflow_id": workflow_id,
                "metric": "success_rate",
                "value": stats["success_rate"],
                "threshold": 0.95
            })

    async def generate_automation_report(self,
                                          period: str = "weekly") -> AutomationReport:
        """Report ROI automazione vs processi manuali."""
        all_workflows = await self.metrics.get_all_workflows(period)

        time_saved_hours = sum(
            (w["baseline_manual_time_min"] - w["avg_execution_time_min"]) *
            w["volume"] / 60
            for w in all_workflows
        )
        cost_saved = time_saved_hours * settings.avg_hourly_cost

        return AutomationReport(
            period=period,
            total_executions=sum(w["volume"] for w in all_workflows),
            success_rate=sum(w["success_rate"] for w in all_workflows) / len(all_workflows),
            time_saved_hours=round(time_saved_hours, 1),
            cost_saved_eur=round(cost_saved, 2),
            top_processes=[w["workflow_id"] for w in sorted(
                all_workflows, key=lambda x: x["volume"], reverse=True)[:5]]
        )
```

---

## 7. n8n Workflow Template (YAML/JSON)

Esempio di workflow n8n per automazione onboarding dipendente:

```json
{
  "name": "Employee Onboarding Automation",
  "nodes": [
    {
      "id": "trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": { "path": "new-employee", "method": "POST" }
    },
    {
      "id": "create_accounts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.IT_SYSTEM_API }}/users",
        "method": "POST",
        "body": {
          "email": "={{ $json.email }}",
          "department": "={{ $json.department }}"
        }
      }
    },
    {
      "id": "send_welcome",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "={{ $json.email }}",
        "subject": "Benvenuto in [Azienda]!",
        "body": "Ciao {{ $json.first_name }}, il tuo account è pronto."
      }
    },
    {
      "id": "update_dto",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.DTO_API_URL }}/twin/events",
        "method": "POST",
        "body": {
          "event_type": "EMPLOYEE_ONBOARDED",
          "entity_id": "={{ $json.employee_id }}",
          "payload": "={{ $json }}"
        }
      }
    }
  ],
  "connections": {
    "trigger": { "main": [["create_accounts"]] },
    "create_accounts": { "main": [["send_welcome"]] },
    "send_welcome": { "main": [["update_dto"]] }
  }
}
```

---

## 8. Checklist Implementazione BPA

### Fase 0 — Discovery (Settimana 0)
- [ ] Interviste stakeholder sui processi prioritari da automatizzare
- [ ] Process mapping as-is (BPMN o swim lane)
- [ ] Calcolo baseline KPI (tempo medio, error rate, costo)
- [ ] Identificazione sorgenti e destinazioni dati
- [ ] Analisi compliance e vincoli normativi

### Fase 1 — Foundation (Settimana 1-2)
- [ ] Setup workflow engine (n8n dev + prod)
- [ ] Implementare schema workflow base riutilizzabile
- [ ] Connettori API per sistemi prioritari
- [ ] Sistema secrets management
- [ ] Dashboard monitoring iniziale

### Fase 2 — First Automations (Settimana 3-4)
- [ ] Implementare 2-3 workflow prioritari (quick wins)
- [ ] Test end-to-end in ambiente staging
- [ ] Human-in-the-loop per step di approvazione
- [ ] Error handling e notifiche ops
- [ ] Go-live monitorato con rollback plan

### Fase 3 — AI Integration (Settimana 5-6)
- [ ] Integrare AI Agent sui decision point complessi
- [ ] Fine-tuning prompt su casistica aziendale reale
- [ ] A/B test: AI routing vs regole statiche
- [ ] Validate accuracy AI decisions (> 90% target)

### Fase 4 — DTO Integration (Settimana 7-8)
- [ ] Pubblicazione eventi BPA al Digital Twin
- [ ] Ricezione alert dal DTO (SLA breach → trigger workflow)
- [ ] Chiusura del loop: DTO vede → BPA agisce → DTO misura
- [ ] Report ROI automazione mensile automatizzato

---

## 9. Business Rules Separata dal Codice

```yaml
# rules/approval_thresholds.yaml
# Soglie approvazione fatture (modificabile senza deploy)

approval_tiers:
  - max_amount_eur: 1000
    approver_role: "team_lead"
    auto_approve: true
    conditions:
      - vendor_sla_compliance_min: 0.95
      - vendor_history_months_min: 6

  - max_amount_eur: 10000
    approver_role: "dept_manager"
    auto_approve: false
    sla_hours: 24

  - max_amount_eur: 50000
    approver_role: "finance_director"
    auto_approve: false
    sla_hours: 48
    requires_ai_assessment: true

  - max_amount_eur: 999999999
    approver_role: "cfo"
    auto_approve: false
    sla_hours: 72
    requires_ai_assessment: true
    requires_legal_review: true

escalation_chain:
  - level: 1
    role: "dept_manager"
    sla_breach_hours: 24
  - level: 2
    role: "finance_director"
    sla_breach_hours: 48
  - level: 3
    role: "cfo"
    sla_breach_hours: 72
```

---

## 10. Metriche di Successo BPA

| Metrica | Baseline | Target | Misurazione |
|---------|----------|--------|-------------|
| Execution Time | manuale | -70% | Avg msec per workflow |
| Error Rate | 5-15% manuale | < 2% | Errori / totale esecuzioni |
| SLA Compliance | 60-80% | > 95% | Completamenti entro deadline |
| Cost per Process | variabile | -50% | EUR / esecuzione |
| Manual Touchpoints | 10+ | < 3 | Step con intervento umano |
| Time-to-Automation | n/a | < 2 week | Da spec a go-live |
