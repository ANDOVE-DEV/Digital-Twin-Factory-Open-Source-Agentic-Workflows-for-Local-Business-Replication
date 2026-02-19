# DTO — Digital Twin of an Organization
## Implementation Playbook

---

## 1. Architettura di Riferimento

### Vista Layered (4-Layer Architecture)

```
┌──────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                           │
│   Dashboard React/D3.js · REST API · GraphQL · Simulator    │
├──────────────────────────────────────────────────────────────┤
│                  INTELLIGENCE LAYER                          │
│    LLM Engine · Anomaly Detection · Forecasting · RAG       │
├──────────────────────────────────────────────────────────────┤
│                    MODEL LAYER                               │
│    Ontologia Grafo · State Machine · Event Sourcing         │
├──────────────────────────────────────────────────────────────┤
│                    DATA LAYER                                │
│    ERP · CRM · HRMS · IoT Sensors · File/CSV · Webhooks    │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Stack Tecnologico Raccomandato

| Componente | Tecnologia | Motivazione |
|------------|-----------|-------------|
| Grafo organizzativo | Neo4j / Azure Digital Twins | Relazioni native, Cypher query |
| Time-series KPI | InfluxDB / TimescaleDB | Performance su serie temporali |
| Event streaming | Apache Kafka / Redis Streams | Sync real-time scalabile |
| Intelligence | LangChain + OpenAI GPT-4o | RAG su knowledge base aziendale |
| API | FastAPI (Python) | Async, WebSocket support |
| Frontend | React + D3.js | Visualizzazione grafo interattiva |
| Orchestration | n8n / Temporal | Workflow automation integrata |
| Auth & RBAC | Keycloak / Auth0 | Sicurezza enterprise |

---

## 3. Schema Dati: Entità Core

```python
# ============================================================
# ENTITY DEFINITIONS — DTO Core Ontology
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class NodeType(Enum):
    ORGANIZATION = "Organization"
    UNIT = "OrganizationUnit"
    PERSON = "Person"
    ROLE = "Role"
    PROCESS = "Process"
    RESOURCE = "Resource"
    KPI = "KPI"
    SYSTEM = "ITSystem"

@dataclass
class OrgNode:
    """Nodo base dell'ontologia organizzativa."""
    id: str
    type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

@dataclass
class OrgEdge:
    """Relazione tra nodi del twin."""
    source_id: str
    target_id: str
    relation: str          # BELONGS_TO, MANAGES, EXECUTES, DEPENDS_ON
    properties: Dict[str, Any] = field(default_factory=dict)
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None

@dataclass
class KPIDefinition:
    """Definizione di un indicatore di performance."""
    id: str
    name: str
    unit: str              # %, EUR, count, days, ...
    owner_node_id: str     # Chi è responsabile di questo KPI
    target: float
    warning_threshold: float
    critical_threshold: float
    calculation_formula: str    # "revenue / headcount"
    update_frequency: str       # "realtime", "daily", "weekly"

@dataclass
class KPISnapshot:
    """Valore puntuale di un KPI nel tempo."""
    kpi_id: str
    value: float
    timestamp: datetime
    source: str            # "ERP", "manual", "calculated"
    confidence: float = 1.0
```

---

## 4. Data Ingestion Layer

### 4.1 Connettore ERP (SAP / Oracle)

```python
import asyncio
from typing import AsyncGenerator

class ERPConnector:
    """Connettore per sistemi ERP enterprise."""

    def __init__(self, config: ERPConfig):
        self.config = config
        self.session = None

    async def stream_changes(self) -> AsyncGenerator[OrgEvent, None]:
        """Streaming CDC via DB triggers o API delta."""
        async with self.session.get(f"{self.config.base_url}/delta") as resp:
            async for line in resp.content:
                event = self._parse_erp_event(line)
                if event:
                    yield event

    def _parse_erp_event(self, raw: bytes) -> Optional[OrgEvent]:
        data = json.loads(raw)
        return OrgEvent(
            event_id=data["id"],
            event_type=data["type"],       # "EMPLOYEE_HIRED", "DEPT_RESTRUCTURED"
            entity_id=data["entity_id"],
            payload=data["payload"],
            source="ERP",
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
```

### 4.2 Connettore CRM (Salesforce)

```python
class SalesforceConnector:
    """Sincronizza dati clienti e pipeline → twin commerciale."""

    async def sync_pipeline_kpis(self) -> List[KPISnapshot]:
        opportunities = await self._fetch_open_opportunities()
        return [
            KPISnapshot(
                kpi_id="pipeline_value",
                value=sum(o.amount for o in opportunities),
                timestamp=datetime.utcnow(),
                source="Salesforce"
            ),
            KPISnapshot(
                kpi_id="pipeline_count",
                value=len(opportunities),
                timestamp=datetime.utcnow(),
                source="Salesforce"
            )
        ]
```

---

## 5. Model Layer: Graph Engine

### 5.1 Neo4j Graph Manager

```python
from neo4j import AsyncGraphDatabase

class TwinGraphManager:
    """Gestisce il grafo organizzativo su Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def upsert_node(self, node: OrgNode) -> None:
        async with self.driver.session() as session:
            await session.run("""
                MERGE (n {id: $id})
                SET n += $props
                SET n.type = $type
                SET n.updated_at = datetime()
                SET n.version = n.version + 1
            """, id=node.id, type=node.type.value, props=node.properties)

    async def create_relationship(self, edge: OrgEdge) -> None:
        query = f"""
            MATCH (a {{id: $src}}), (b {{id: $tgt}})
            MERGE (a)-[r:{edge.relation}]->(b)
            SET r += $props
        """
        async with self.driver.session() as session:
            await session.run(query, src=edge.source_id,
                              tgt=edge.target_id, props=edge.properties)

    async def query_bottlenecks(self) -> List[Dict]:
        """Identifica processi che violano SLA."""
        async with self.driver.session() as session:
            result = await session.run("""
                MATCH (p:Process)-[:DEPENDS_ON]->(dep:Process)
                WHERE dep.avg_duration_days > dep.sla_days
                RETURN p.name AS process,
                       dep.name AS bottleneck,
                       dep.avg_duration_days AS actual,
                       dep.sla_days AS target,
                       (dep.avg_duration_days - dep.sla_days) AS delay_days
                ORDER BY delay_days DESC
                LIMIT 10
            """)
            return [dict(r) for r in result]

    async def create_snapshot(self, label: str) -> str:
        """Snapshot del twin per simulazioni what-if."""
        snapshot_id = f"snap_{label}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        async with self.driver.session() as session:
            await session.run("""
                MATCH (n)
                WITH collect(n) as nodes
                CREATE (snap:Snapshot {id: $snap_id, label: $label, created_at: datetime()})
                SET snap.data = apoc.convert.toJson(nodes)
            """, snap_id=snapshot_id, label=label)
        return snapshot_id
```

---

## 6. Intelligence Layer

### 6.1 KPI Anomaly Detector

```python
import numpy as np
from scipy import stats

class KPIAnomalyDetector:
    """Rileva anomalie KPI usando Z-score adattivo."""

    def __init__(self, window_days: int = 30):
        self.window_days = window_days

    def detect_anomaly(self, kpi: KPIDefinition,
                       history: List[KPISnapshot],
                       current: KPISnapshot) -> AnomalyReport:
        values = [s.value for s in history[-self.window_days:]]
        if len(values) < 7:
            return AnomalyReport(is_anomaly=False, reason="Insufficient history")

        mean = np.mean(values)
        std = np.std(values)
        z_score = abs((current.value - mean) / std) if std > 0 else 0

        is_anomaly = z_score > 2.5
        severity = "CRITICAL" if z_score > 3.5 else "HIGH" if z_score > 2.5 else "OK"

        return AnomalyReport(
            kpi_id=kpi.id,
            is_anomaly=is_anomaly,
            severity=severity,
            z_score=round(z_score, 2),
            current_value=current.value,
            baseline_mean=round(mean, 2),
            baseline_std=round(std, 2),
            detected_at=datetime.utcnow()
        )
```

### 6.2 LLM Insight Engine (RAG su Grafo)

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import Neo4jVector

class DTOInsightEngine:
    """Genera insight narrativi sul twin tramite LLM + RAG."""

    def __init__(self, graph_manager: TwinGraphManager, llm):
        self.graph = graph_manager
        self.llm = llm
        self.vector_store = Neo4jVector.from_existing_graph(
            llm.embeddings,
            url=graph_manager.driver._uri,
            node_label="Process",
            text_node_properties=["name", "description", "kpi_summary"]
        )

    async def explain_anomaly(self, kpi: KPIDefinition,
                               anomaly: AnomalyReport) -> str:
        """Genera spiegazione human-readable di un'anomalia KPI."""
        context = await self.graph.get_kpi_context(kpi.id)
        prompt = f"""
        Sei un analista aziendale esperto. Il KPI "{kpi.name}" ha mostrato un'anomalia.
        
        Dati:
        - Valore corrente: {anomaly.current_value} {kpi.unit}
        - Media storica (30gg): {anomaly.baseline_mean}
        - Z-score: {anomaly.z_score}
        - Responsabile: {context.get('owner')}
        - Processi correlati: {context.get('related_processes')}
        
        Fornisci una spiegazione concisa (max 3 frasi) delle possibili cause
        e una raccomandazione immediata.
        """
        return await self.llm.ainvoke(prompt)

    async def generate_weekly_report(self) -> str:
        """Genera report settimanale del twin in linguaggio naturale."""
        summary = await self.graph.get_twin_summary()
        anomalies = await self.graph.get_recent_anomalies(days=7)
        bottlenecks = await self.graph.query_bottlenecks()

        return await self.llm.ainvoke(f"""
        Genera un executive summary settimanale del Digital Twin Organizzativo.
        
        Dati:
        - Summary organizzativo: {summary}
        - Anomalie rilevate (7gg): {anomalies}
        - Top bottleneck processi: {bottlenecks}
        
        Struttura: 1) Highlights positivi, 2) Criticità, 3) Azioni raccomandate.
        Tono: professionale, conciso, orientato alle decisioni.
        Max 300 parole.
        """)
```

---

## 7. API Layer (FastAPI)

```python
from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DTO API", version="1.0.0")

@app.get("/twin/structure")
async def get_org_structure(
    depth: int = 3,
    unit_id: Optional[str] = None,
    graph: TwinGraphManager = Depends(get_graph)
):
    """Ritorna la struttura organizzativa come grafo JSON."""
    return await graph.get_org_tree(root_id=unit_id, depth=depth)

@app.post("/twin/simulate")
async def run_simulation(scenario: ScenarioRequest,
                          graph: TwinGraphManager = Depends(get_graph)):
    """Esegue una simulazione what-if e ritorna l'analisi impatto."""
    snapshot_id = await graph.create_snapshot("pre_simulation")
    try:
        await graph.apply_scenario(scenario)
        impact = await graph.analyze_impact(scenario.metrics)
        return {"snapshot_id": snapshot_id, "impact": impact}
    finally:
        await graph.restore_snapshot(snapshot_id)

@app.websocket("/twin/stream")
async def twin_stream(websocket: WebSocket,
                       sync: TwinSynchronizer = Depends(get_sync)):
    """WebSocket per aggiornamenti real-time del twin."""
    await websocket.accept()
    async for event in sync.event_stream():
        await websocket.send_json(event.dict())

@app.get("/twin/kpis/{kpi_id}/insights")
async def get_kpi_insights(kpi_id: str,
                            engine: DTOInsightEngine = Depends(get_insight_engine)):
    """Insight AI su un KPI specifico."""
    anomaly = await engine.get_latest_anomaly(kpi_id)
    explanation = await engine.explain_anomaly(kpi_id, anomaly)
    return {"kpi_id": kpi_id, "anomaly": anomaly, "insight": explanation}
```

---

## 8. Checklist Implementazione

### Fase 1 — Foundation (Settimana 1-2)
- [ ] Definire scope del twin (reparti, processi, KPI in scope)
- [ ] Censire le sorgenti dati e i relativi owner
- [ ] Progettare ontologia personalizzata (estendere schema base)
- [ ] Setup Neo4j (o Azure Digital Twins) + schema iniziale
- [ ] Implementare connettori dati prioritari (almeno HR + Finance)

### Fase 2 — Synchronization (Settimana 3-4)
- [ ] Implementare event streaming (Kafka o Redis Streams)
- [ ] CDC dai DB sorgente (Debezium per PostgreSQL/MySQL)
- [ ] Webhook integration per sistemi SaaS
- [ ] Idempotenza e deduplicazione eventi
- [ ] Audit log di tutte le modifiche al twin

### Fase 3 — Intelligence (Settimana 5-6)
- [ ] Implementare KPI anomaly detection
- [ ] Setup LLM con RAG sul grafo organizzativo
- [ ] Forecasting KPI (ARIMA o Prophet)
- [ ] Alert system con escalation chain

### Fase 4 — Interfaces (Settimana 7-8)
- [ ] API REST/GraphQL documentata (OpenAPI)
- [ ] Dashboard executive con D3.js/Recharts
- [ ] Simulatore scenari what-if
- [ ] Integrazione BPA per closure del loop decisionale

---

## 9. Security & Governance

```yaml
# Configurazione RBAC per il DTO
roles:
  twin_admin:
    - can: [read, write, simulate, delete]
    - on: [all_nodes, all_edges, all_kpis]
  
  executive:
    - can: [read, simulate]
    - on: [org_structure, kpi_aggregated, insights]
    - cannot: [individual_employee_data]
  
  dept_manager:
    - can: [read, simulate]
    - on: [own_department_nodes, own_department_kpis]
  
  data_engineer:
    - can: [read, write]
    - on: [data_layer, connectors]
    - cannot: [simulate, delete_nodes]

data_governance:
  retention_days: 365          # KPI snapshots
  pii_anonymization: true      # Dati personali dipendenti
  audit_log: true              # Ogni modifica al twin
  schema_versioning: true      # Versione ontologia con changelog
```

---

## 10. Metriche di Successo del DTO

| Metrica | Target | Misurazione |
|---------|--------|-------------|
| Data Freshness | < 15 min | Lag tra evento reale e twin update |
| Model Coverage | > 85% | % processi chiave modellati |
| KPI Accuracy | > 92% | Correlazione valore twin vs reale |
| Insight Adoption | > 60% | % insight che generano azioni |
| Simulation ROI | > 3x | Valore decisioni migliorate / costo twin |
