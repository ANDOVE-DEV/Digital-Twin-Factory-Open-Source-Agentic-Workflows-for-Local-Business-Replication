# DTO ↔ BPA Integration
## Loop Chiuso: Sense → Decide → Act → Measure

---

## 1. Filosofia dell'Integrazione

Il **DTO** (Digital Twin of an Organization) e il **BPA** (Business Process Automation)
formano un sistema adattivo a ciclo chiuso, ispirato al modello OODA
(Observe → Orient → Decide → Act):

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FABBRICA DEI DIGITAL TWIN                    │
│                                                                     │
│   ┌──────────────────────┐         ┌──────────────────────────┐    │
│   │        DTO           │         │          BPA             │    │
│   │  Digital Twin of an  │ ──────► │  Business Process        │    │
│   │    Organization      │ EVENTS  │    Automation            │    │
│   │                      │         │                          │    │
│   │  SENSE & MODEL       │ ◄────── │  ACT & EXECUTE           │    │
│   │  - Struttura org.    │ KPI UPD │  - Workflow engine       │    │
│   │  - KPI real-time     │         │  - AI agents             │    │
│   │  - Anomalie          │         │  - Integrazioni          │    │
│   │  - Simulazioni       │         │  - Task umani            │    │
│   └──────────────────────┘         └──────────────────────────┘    │
│            │                                    ▲                   │
│            │         EVENT BUS                  │                   │
│            │    (Redis Streams / Kafka)          │                   │
│            └────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Regola d'oro**: Il DTO non esegue mai azioni sui sistemi reali.
Il BPA non modella mai l'organizzazione. Ciascuno fa la propria parte.

---

## 2. Contratto degli Eventi (Event Schema)

Tutti gli eventi scambiati tra DTO e BPA seguono un contratto unico:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import uuid

class EventDirection(Enum):
    DTO_TO_BPA = "dto→bpa"   # DTO rileva qualcosa, BPA deve agire
    BPA_TO_DTO = "bpa→dto"   # BPA ha eseguito qualcosa, DTO deve aggiornarsi

class EventPriority(Enum):
    CRITICAL = "critical"    # Azione immediata richiesta (< 1 min)
    HIGH     = "high"        # Azione urgente (< 15 min)
    MEDIUM   = "medium"      # Azione pianificata (< 1 ora)
    LOW      = "low"         # Informativo, log + dashboard

@dataclass
class IntegrationEvent:
    """Envelope condiviso DTO ↔ BPA."""
    event_id:      str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type:    str = ""                  # Vedi catalogo sotto
    direction:     EventDirection = EventDirection.DTO_TO_BPA
    priority:      EventPriority  = EventPriority.MEDIUM
    source:        str = ""                  # "dto" | "bpa"
    entity_id:     str = ""                  # ID nodo/processo coinvolto
    entity_type:   str = ""                  # "Process" | "KPI" | "Unit" | "Workflow"
    payload:       Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None     # Lega evento → risposta
    timestamp:     datetime = field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"
```

---

## 3. Catalogo degli Eventi

### 3.1 DTO → BPA (Il Twin rileva, il BPA agisce)

| `event_type` | `priority` | Descrizione | Workflow BPA triggered |
|-------------|-----------|-------------|----------------------|
| `dto.kpi.anomaly_detected` | HIGH | KPI fuori soglia (z-score > 2.5) | `kpi-anomaly-response` |
| `dto.process.sla_breach` | CRITICAL | Processo supera SLA | `sla-escalation-workflow` |
| `dto.process.bottleneck_identified` | MEDIUM | Collo di bottiglia nel grafo | `bottleneck-review-workflow` |
| `dto.org.restructuring_simulated` | LOW | Simulazione completata con risultati | `restructuring-impact-report` |
| `dto.org.vacancy_detected` | MEDIUM | Ruolo scoperto (persona → offboarding) | `hiring-request-workflow` |
| `dto.budget.overrun_predicted` | HIGH | Forecast supera budget | `budget-alert-workflow` |
| `dto.vendor.risk_elevated` | HIGH | Score fornitore sceso sotto soglia | `vendor-review-workflow` |
| `dto.compliance.deadline_approaching` | HIGH | Scadenza compliance < 30 gg | `compliance-check-workflow` |

### 3.2 BPA → DTO (Il BPA esegue, il Twin si aggiorna)

| `event_type` | Descrizione | Aggiornamento DTO |
|-------------|-------------|------------------|
| `bpa.workflow.completed` | Workflow terminato con successo | Aggiorna KPI processo, execution_time |
| `bpa.workflow.failed` | Workflow fallito | Incrementa error_rate KPI |
| `bpa.employee.onboarded` | Nuovo dipendente onboarded | Aggiunge nodo Person + edge BELONGS_TO |
| `bpa.employee.offboarded` | Dipendente offboarded | Rimuove edge, aggiorna headcount |
| `bpa.process.automated` | Nuovo processo automatizzato | Aggiorna automation_level = "full-auto" |
| `bpa.sla.resolved` | Violazione SLA risolta | Aggiorna avg_duration, sla_compliance |
| `bpa.budget.approved` | Budget approvato | Aggiorna budget_remaining nel twin |
| `bpa.contract.renewed` | Contratto fornitore rinnovato | Aggiorna vendor node + expiry_date |
| `bpa.kpi.updated` | BPA riporta KPI misurati | Aggiorna KPISnapshot nel twin |

---

## 4. Event Bus Implementation

### 4.1 Publisher (Redis Streams)

```python
import redis.asyncio as redis
import json
from typing import Optional

class IntegrationEventBus:
    """
    Event bus bidirezionale DTO ↔ BPA.
    Usa Redis Streams per persistenza e replay.
    """

    STREAM_DTO_TO_BPA = "stream:dto-to-bpa"
    STREAM_BPA_TO_DTO = "stream:bpa-to-dto"
    CONSUMER_GROUP    = "digital-twin-factory"

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def publish(self, event: IntegrationEvent) -> str:
        """Pubblica evento sullo stream corretto."""
        stream = (self.STREAM_DTO_TO_BPA
                  if event.direction == EventDirection.DTO_TO_BPA
                  else self.STREAM_BPA_TO_DTO)

        message_id = await self.redis.xadd(
            stream,
            {
                "event_id":      event.event_id,
                "event_type":    event.event_type,
                "priority":      event.priority.value,
                "source":        event.source,
                "entity_id":     event.entity_id,
                "entity_type":   event.entity_type,
                "payload":       json.dumps(event.payload),
                "correlation_id": event.correlation_id or "",
                "timestamp":     event.timestamp.isoformat(),
                "schema_version": event.schema_version
            },
            maxlen=10_000      # Retention: ultimi 10k eventi
        )
        return message_id

    async def subscribe(self, direction: EventDirection,
                         consumer_name: str,
                         batch_size: int = 10):
        """
        Consumer loop — non-blocking, async.
        Restituisce eventi in batch per processing.
        """
        stream = (self.STREAM_DTO_TO_BPA
                  if direction == EventDirection.DTO_TO_BPA
                  else self.STREAM_BPA_TO_DTO)

        # Crea consumer group se non esiste
        try:
            await self.redis.xgroup_create(
                stream, self.CONSUMER_GROUP, id="$", mkstream=True
            )
        except redis.ResponseError:
            pass  # Group già esistente

        while True:
            messages = await self.redis.xreadgroup(
                self.CONSUMER_GROUP,
                consumer_name,
                {stream: ">"},
                count=batch_size,
                block=1000          # ms di attesa se stream vuoto
            )

            if messages:
                for stream_name, entries in messages:
                    for msg_id, data in entries:
                        event = self._deserialize(data)
                        yield msg_id, event

    async def acknowledge(self, stream_key: str, msg_id: str):
        """Conferma elaborazione evento (rimuove da pending)."""
        stream = (self.STREAM_DTO_TO_BPA
                  if "dto-to-bpa" in stream_key
                  else self.STREAM_BPA_TO_DTO)
        await self.redis.xack(stream, self.CONSUMER_GROUP, msg_id)

    def _deserialize(self, data: dict) -> IntegrationEvent:
        return IntegrationEvent(
            event_id=data["event_id"],
            event_type=data["event_type"],
            priority=EventPriority(data["priority"]),
            source=data["source"],
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            payload=json.loads(data["payload"]),
            correlation_id=data.get("correlation_id") or None,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            schema_version=data["schema_version"]
        )
```

---

## 5. DTO Side: Event Publisher

```python
class DTOEventPublisher:
    """
    Componente DTO che pubblica eventi verso BPA
    quando il twin rileva situazioni che richiedono azione.
    """

    def __init__(self, bus: IntegrationEventBus):
        self.bus = bus

    async def on_kpi_anomaly(self, kpi: KPIDefinition,
                              anomaly: AnomalyReport) -> str:
        """Anomalia KPI rilevata → notifica BPA."""
        event = IntegrationEvent(
            event_type="dto.kpi.anomaly_detected",
            direction=EventDirection.DTO_TO_BPA,
            priority=EventPriority.CRITICAL if anomaly.severity == "CRITICAL"
                     else EventPriority.HIGH,
            source="dto",
            entity_id=kpi.id,
            entity_type="KPI",
            payload={
                "kpi_name":       kpi.name,
                "kpi_unit":       kpi.unit,
                "current_value":  anomaly.current_value,
                "baseline_mean":  anomaly.baseline_mean,
                "z_score":        anomaly.z_score,
                "severity":       anomaly.severity,
                "owner_unit_id":  kpi.owner_node_id,
                "recommended_action": anomaly.recommendation
            }
        )
        return await self.bus.publish(event)

    async def on_sla_breach(self, process_id: str,
                             actual_days: float,
                             sla_days: float,
                             owner_unit_id: str) -> str:
        """Violazione SLA processo → BPA avvia escalation."""
        delay = actual_days - sla_days
        priority = EventPriority.CRITICAL if delay > sla_days * 0.5 \
                   else EventPriority.HIGH

        event = IntegrationEvent(
            event_type="dto.process.sla_breach",
            direction=EventDirection.DTO_TO_BPA,
            priority=priority,
            source="dto",
            entity_id=process_id,
            entity_type="Process",
            payload={
                "process_id":     process_id,
                "actual_days":    actual_days,
                "sla_days":       sla_days,
                "delay_days":     round(delay, 1),
                "owner_unit_id":  owner_unit_id,
                "breach_pct":     round((delay / sla_days) * 100, 1)
            }
        )
        return await self.bus.publish(event)

    async def on_vacancy_detected(self, unit_id: str,
                                   role_id: str,
                                   role_title: str) -> str:
        """Ruolo scoperto rilevato dal twin → BPA avvia hiring."""
        event = IntegrationEvent(
            event_type="dto.org.vacancy_detected",
            direction=EventDirection.DTO_TO_BPA,
            priority=EventPriority.MEDIUM,
            source="dto",
            entity_id=role_id,
            entity_type="Role",
            payload={
                "unit_id":    unit_id,
                "role_id":    role_id,
                "role_title": role_title,
                "detected_at": datetime.utcnow().isoformat()
            }
        )
        return await self.bus.publish(event)

    async def on_budget_overrun_predicted(self, unit_id: str,
                                           forecast_eur: float,
                                           budget_eur: float) -> str:
        """Forecast supera budget → BPA avvia alert finanziario."""
        overrun_pct = ((forecast_eur - budget_eur) / budget_eur) * 100
        event = IntegrationEvent(
            event_type="dto.budget.overrun_predicted",
            direction=EventDirection.DTO_TO_BPA,
            priority=EventPriority.HIGH,
            source="dto",
            entity_id=unit_id,
            entity_type="OrganizationUnit",
            payload={
                "unit_id":       unit_id,
                "forecast_eur":  forecast_eur,
                "budget_eur":    budget_eur,
                "overrun_pct":   round(overrun_pct, 1),
                "forecast_date": datetime.utcnow().isoformat()
            }
        )
        return await self.bus.publish(event)
```

---

## 6. BPA Side: Event Consumer & Dispatcher

```python
class BPAEventConsumer:
    """
    Componente BPA che consuma eventi dal DTO
    e avvia il workflow corretto in risposta.
    """

    def __init__(self, bus: IntegrationEventBus,
                 workflow_engine,
                 dto_updater: 'DTOUpdater'):
        self.bus = bus
        self.engine = workflow_engine
        self.dto_updater = dto_updater

        # Router: event_type → handler
        self.handlers = {
            "dto.kpi.anomaly_detected":       self._handle_kpi_anomaly,
            "dto.process.sla_breach":         self._handle_sla_breach,
            "dto.org.vacancy_detected":        self._handle_vacancy,
            "dto.budget.overrun_predicted":    self._handle_budget_overrun,
            "dto.vendor.risk_elevated":        self._handle_vendor_risk,
            "dto.compliance.deadline_approaching": self._handle_compliance,
        }

    async def start(self):
        """Loop principale consumer — gira in background."""
        async for msg_id, event in self.bus.subscribe(
            EventDirection.DTO_TO_BPA, consumer_name="bpa-main"
        ):
            try:
                handler = self.handlers.get(event.event_type)
                if handler:
                    await handler(event)
                else:
                    print(f"[BPA Consumer] Evento non gestito: {event.event_type}")

                await self.bus.acknowledge("dto-to-bpa", msg_id)

            except Exception as e:
                print(f"[BPA Consumer] Errore su {event.event_id}: {e}")
                # Non fare ACK → evento resta in pending per retry

    # ── HANDLERS ────────────────────────────────────────────────

    async def _handle_kpi_anomaly(self, event: IntegrationEvent):
        """KPI out-of-bound → avvia workflow di risposta."""
        await self.engine.start_workflow(
            workflow_name="kpi-anomaly-response",
            input={
                "kpi_id":        event.entity_id,
                "kpi_name":      event.payload["kpi_name"],
                "severity":      event.payload["severity"],
                "current_value": event.payload["current_value"],
                "owner_unit_id": event.payload["owner_unit_id"],
                "correlation_id": event.event_id
            }
        )

    async def _handle_sla_breach(self, event: IntegrationEvent):
        """SLA violato → escalation immediata."""
        priority = event.priority.value

        if priority == "critical":
            # Notifica immediata + task urgente
            await self.engine.start_workflow(
                workflow_name="sla-critical-escalation",
                input={**event.payload, "correlation_id": event.event_id}
            )
        else:
            # Escalation standard con SLA di risposta
            await self.engine.start_workflow(
                workflow_name="sla-escalation-workflow",
                input={**event.payload, "correlation_id": event.event_id}
            )

    async def _handle_vacancy(self, event: IntegrationEvent):
        """Ruolo scoperto → workflow hiring request."""
        await self.engine.start_workflow(
            workflow_name="hiring-request-workflow",
            input={
                "role_id":    event.entity_id,
                "role_title": event.payload["role_title"],
                "unit_id":    event.payload["unit_id"],
                "correlation_id": event.event_id
            }
        )

    async def _handle_budget_overrun(self, event: IntegrationEvent):
        """Budget forecast breach → alert finanziario."""
        await self.engine.start_workflow(
            workflow_name="budget-alert-workflow",
            input={**event.payload, "correlation_id": event.event_id}
        )

    async def _handle_vendor_risk(self, event: IntegrationEvent):
        """Vendor risk elevato → review workflow."""
        await self.engine.start_workflow(
            workflow_name="vendor-review-workflow",
            input={**event.payload, "correlation_id": event.event_id}
        )

    async def _handle_compliance(self, event: IntegrationEvent):
        """Scadenza compliance → checklist workflow."""
        await self.engine.start_workflow(
            workflow_name="compliance-check-workflow",
            input={**event.payload, "correlation_id": event.event_id}
        )
```

---

## 7. BPA Side: DTO Updater (BPA → DTO)

```python
class DTOUpdater:
    """
    Componente BPA che aggiorna il Digital Twin
    dopo ogni esecuzione di workflow.
    """

    def __init__(self, dto_api_url: str, bus: IntegrationEventBus):
        self.dto_url = dto_api_url
        self.bus = bus

    async def on_workflow_completed(self, workflow_id: str,
                                     result: WorkflowResult,
                                     entity_id: str,
                                     entity_type: str):
        """Ogni workflow completato pubblica il risultato al DTO."""
        event = IntegrationEvent(
            event_type="bpa.workflow.completed",
            direction=EventDirection.BPA_TO_DTO,
            priority=EventPriority.LOW,
            source="bpa",
            entity_id=entity_id,
            entity_type=entity_type,
            payload={
                "workflow_id":       workflow_id,
                "status":            result.status,
                "execution_time_sec": result.execution_time_sec,
                "output_summary":    result.output
            },
            correlation_id=result.output.get("correlation_id")
        )
        await self.bus.publish(event)

    async def on_employee_onboarded(self, employee_data: dict):
        """Aggiunge nuovo dipendente al grafo DTO."""
        event = IntegrationEvent(
            event_type="bpa.employee.onboarded",
            direction=EventDirection.BPA_TO_DTO,
            priority=EventPriority.MEDIUM,
            source="bpa",
            entity_id=employee_data["employee_id"],
            entity_type="Person",
            payload=employee_data
        )
        await self.bus.publish(event)

        # Anche chiamata diretta all'API DTO per aggiornamento immediato
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.dto_url}/twin/events",
                              json=event.__dict__,
                              timeout=10)

    async def on_process_automated(self, process_id: str,
                                    automation_level: str,
                                    new_avg_time_days: float):
        """Aggiorna il livello di automazione del processo nel DTO."""
        event = IntegrationEvent(
            event_type="bpa.process.automated",
            direction=EventDirection.BPA_TO_DTO,
            priority=EventPriority.LOW,
            source="bpa",
            entity_id=process_id,
            entity_type="Process",
            payload={
                "process_id":        process_id,
                "automation_level":  automation_level,
                "new_avg_time_days": new_avg_time_days,
                "automated_at":      datetime.utcnow().isoformat()
            }
        )
        await self.bus.publish(event)

    async def on_sla_resolved(self, process_id: str,
                               resolution_time_days: float):
        """Aggiorna SLA del processo nel DTO dopo risoluzione."""
        event = IntegrationEvent(
            event_type="bpa.sla.resolved",
            direction=EventDirection.BPA_TO_DTO,
            priority=EventPriority.MEDIUM,
            source="bpa",
            entity_id=process_id,
            entity_type="Process",
            payload={
                "process_id":           process_id,
                "resolution_time_days": resolution_time_days,
                "resolved_at":          datetime.utcnow().isoformat()
            }
        )
        await self.bus.publish(event)
```

---

## 8. DTO Side: Event Consumer (BPA → DTO)

```python
class DTOEventConsumer:
    """
    Componente DTO che riceve gli aggiornamenti dal BPA
    e aggiorna il modello del twin di conseguenza.
    """

    def __init__(self, bus: IntegrationEventBus,
                 graph: TwinGraphManager,
                 kpi_store: KPIStore):
        self.bus = bus
        self.graph = graph
        self.kpi_store = kpi_store

        self.handlers = {
            "bpa.workflow.completed":    self._update_process_kpi,
            "bpa.workflow.failed":       self._record_workflow_error,
            "bpa.employee.onboarded":    self._add_person_node,
            "bpa.employee.offboarded":   self._remove_person_edges,
            "bpa.process.automated":     self._update_automation_level,
            "bpa.sla.resolved":          self._update_sla_metrics,
            "bpa.budget.approved":       self._update_budget_node,
            "bpa.contract.renewed":      self._update_vendor_node,
            "bpa.kpi.updated":           self._upsert_kpi_snapshot,
        }

    async def start(self):
        """Loop consumer per aggiornamenti BPA → DTO."""
        async for msg_id, event in self.bus.subscribe(
            EventDirection.BPA_TO_DTO, consumer_name="dto-main"
        ):
            try:
                handler = self.handlers.get(event.event_type)
                if handler:
                    await handler(event)
                await self.bus.acknowledge("bpa-to-dto", msg_id)
            except Exception as e:
                print(f"[DTO Consumer] Errore: {e}")

    async def _add_person_node(self, event: IntegrationEvent):
        node = OrgNode(
            id=event.entity_id,
            type=NodeType.PERSON,
            label=event.payload.get("anonymized_name", event.entity_id),
            properties={
                "unit_id":    event.payload.get("unit_id"),
                "seniority":  event.payload.get("seniority"),
                "fte":        event.payload.get("fte", 1.0),
                "join_date":  event.payload.get("join_date"),
            }
        )
        await self.graph.upsert_node(node)
        await self.graph.create_relationship(OrgEdge(
            source_id=event.entity_id,
            target_id=event.payload["unit_id"],
            relation="BELONGS_TO",
            properties={"since_date": event.payload.get("join_date")}
        ))

    async def _update_automation_level(self, event: IntegrationEvent):
        """Aggiorna il livello automazione di un processo nel twin."""
        await self.graph.update_node_property(
            node_id=event.entity_id,
            properties={
                "automation_level":   event.payload["automation_level"],
                "avg_duration_days":  event.payload["new_avg_time_days"],
                "last_automated_at":  event.payload["automated_at"]
            }
        )

    async def _update_sla_metrics(self, event: IntegrationEvent):
        """Aggiorna metriche SLA del processo nel twin."""
        history = await self.kpi_store.get_history(
            f"process.{event.entity_id}.resolution_time", days=30
        )
        new_avg = (sum(h.value for h in history) +
                   event.payload["resolution_time_days"]) / (len(history) + 1)

        await self.graph.update_node_property(
            node_id=event.entity_id,
            properties={"avg_duration_days": round(new_avg, 2)}
        )

    async def _upsert_kpi_snapshot(self, event: IntegrationEvent):
        """Aggiorna un KPI nel twin con il valore misurato dal BPA."""
        snapshot = KPISnapshot(
            kpi_id=event.entity_id,
            value=event.payload["value"],
            timestamp=datetime.utcnow(),
            source=f"bpa.{event.payload.get('workflow_id', 'unknown')}"
        )
        await self.kpi_store.save_snapshot(snapshot)
```

---

## 9. Sequenze End-to-End

### Scenario A: SLA Breach → Escalation → Risoluzione → Twin Update

```
1. [DTO] KPI "process.invoice_approval.avg_time" supera soglia
   │
2. [DTO] DTOEventPublisher.on_sla_breach(process_id, actual=8.2, sla=5.0)
   │
3. [EventBus] Evento "dto.process.sla_breach" priority=CRITICAL pubblicato
   │
4. [BPA] BPAEventConsumer._handle_sla_breach() riceve evento
   │
5. [BPA] Avvia "sla-critical-escalation" workflow:
   │       → Notifica dept_manager via Slack (< 1 min)
   │       → Crea task urgente in task manager
   │       → Se non risolto in 2h → escalate to CFO
   │
6. [BPA] Manager riassegna risorse → processo torna in SLA
   │
7. [BPA] DTOUpdater.on_sla_resolved(process_id, resolution_time=1.5)
   │
8. [EventBus] Evento "bpa.sla.resolved" pubblicato
   │
9. [DTO] DTOEventConsumer._update_sla_metrics() aggiorna avg_duration
   │
10. [DTO] KPI monitor vede miglioramento → nessun nuovo alert ✓
```

### Scenario B: Dipendente in Uscita → Twin Coherence

```
1. [BPA] HRMS webhook: data_fine_rapporto = oggi
   │
2. [BPA] Avvia "employee-offboarding-workflow"
   │       → Disabilita account AD
   │       → Revoca accessi sistemi
   │       → Recovery asset
   │
3. [BPA] DTOUpdater.on_employee_offboarded(employee_id, unit_id)
   │
4. [EventBus] Evento "bpa.employee.offboarded" pubblicato
   │
5. [DTO] DTOEventConsumer._remove_person_edges():
   │       → Rimuove edge BELONGS_TO
   │       → Marca Role come vacancy
   │       → Aggiorna headcount OrganizationUnit
   │
6. [DTO] Headcount sotto threshold → on_vacancy_detected(role_id)
   │
7. [EventBus] Evento "dto.org.vacancy_detected"
   │
8. [BPA] BPAEventConsumer._handle_vacancy():
         → Avvia "hiring-request-workflow"
         → Notifica HR manager
         → Crea job posting draft ✓
```

---

## 10. Setup Rapido dell'Integrazione

```python
# main.py — Bootstrap Fabbrica dei Digital Twin

import asyncio

async def main():
    # 1. Event Bus condiviso
    bus = IntegrationEventBus(redis_url="redis://localhost:6379")

    # 2. DTO Components
    graph = TwinGraphManager(uri="bolt://localhost:7687",
                              user="neo4j", password="password")
    kpi_store   = KPIStore(timescale_dsn="postgresql://...")
    dto_publisher = DTOEventPublisher(bus=bus)
    dto_consumer  = DTOEventConsumer(bus=bus, graph=graph,
                                     kpi_store=kpi_store)

    # 3. BPA Components
    workflow_engine = TemporalEngine(host="localhost:7233")
    dto_updater   = DTOUpdater(dto_api_url="http://dto-api:8000", bus=bus)
    bpa_consumer  = BPAEventConsumer(bus=bus,
                                     workflow_engine=workflow_engine,
                                     dto_updater=dto_updater)

    # 4. Avvia entrambi i consumer in parallelo
    await asyncio.gather(
        dto_consumer.start(),    # BPA → DTO updates
        bpa_consumer.start(),    # DTO → BPA triggers
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 11. Configurazione (config/integration.yaml)

```yaml
integration:
  event_bus:
    type: redis_streams             # redis_streams | kafka
    redis_url: ${REDIS_URL}
    stream_retention_max: 10000     # Ultimi N eventi in memoria
    consumer_group: digital-twin-factory
    batch_size: 10
    block_timeout_ms: 1000

  dto:
    api_url: ${DTO_API_URL}
    graph_uri: ${NEO4J_URI}
    kpi_store_dsn: ${TIMESCALE_DSN}

  bpa:
    workflow_engine: temporal       # temporal | n8n
    temporal_host: ${TEMPORAL_HOST}
    n8n_url: ${N8N_URL}
    n8n_api_key: ${N8N_API_KEY}

  retry:
    max_attempts: 3
    backoff_seconds: [1, 5, 30]    # Exponential backoff

  monitoring:
    log_all_events: true
    alert_on_consumer_lag_sec: 60   # Alert se consumer è > 60s in ritardo
    dead_letter_stream: stream:dlq  # Fallback per eventi non elaborati
```
