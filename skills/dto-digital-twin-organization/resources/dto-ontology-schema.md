# DTO — Ontology Schema Standard
## Schema Entità e Relazioni del Digital Twin Organizzativo

---

## Nodi (Node Types)

### Organization
Il nodo radice dell'intera gerarchia.

```json
{
  "type": "Organization",
  "required": ["id", "name", "industry", "country"],
  "properties": {
    "id":           "string (UUID)",
    "name":         "string",
    "industry":     "string (NAICS/ATECO code)",
    "country":      "string (ISO 3166-1)",
    "size":         "enum: micro | small | medium | large | enterprise",
    "revenue":      "float (EUR)",
    "headcount":    "integer",
    "founded_year": "integer",
    "twin_version": "string (semver)"
  }
}
```

### OrganizationUnit
Reparto, divisione, business unit, team.

```json
{
  "type": "OrganizationUnit",
  "required": ["id", "name", "unit_type", "parent_id"],
  "properties": {
    "id":           "string (UUID)",
    "name":         "string",
    "unit_type":    "enum: division | department | team | squad",
    "parent_id":    "string (FK → OrganizationUnit or Organization)",
    "cost_center":  "string",
    "budget":       "float (EUR/anno)",
    "headcount":    "integer",
    "location":     "string",
    "is_virtual":   "boolean"
  }
}
```

### Person
Dipendente, collaboratore, consulente.

```json
{
  "type": "Person",
  "required": ["id", "employee_id", "unit_id"],
  "properties": {
    "id":              "string (UUID)",
    "employee_id":     "string (da HRMS — NON usare dati PII diretti)",
    "anonymized_name": "string (opzionale, solo per admin)",
    "seniority":       "enum: junior | mid | senior | lead | principal",
    "fte":             "float (0.5 = part-time)",
    "join_date":       "date",
    "unit_id":         "string (FK → OrganizationUnit)",
    "skills":          "array[string]",
    "cost_annual":     "float (EUR — aggregato, non salario individuale)"
  }
}
```

### Role
Posizione organizzativa (separata dalla persona).

```json
{
  "type": "Role",
  "required": ["id", "title", "unit_id"],
  "properties": {
    "id":            "string (UUID)",
    "title":         "string",
    "unit_id":       "string (FK → OrganizationUnit)",
    "level":         "integer (1=entry, 5=executive)",
    "is_management": "boolean",
    "headcount_max": "integer",
    "responsibilities": "array[string]",
    "required_skills":  "array[string]"
  }
}
```

### Process
Processo aziendale, workflow, procedura.

```json
{
  "type": "Process",
  "required": ["id", "name", "owner_unit_id"],
  "properties": {
    "id":              "string (UUID)",
    "name":            "string",
    "description":     "string",
    "owner_unit_id":   "string (FK → OrganizationUnit)",
    "process_type":    "enum: core | support | management | innovation",
    "status":          "enum: active | deprecated | draft",
    "sla_days":        "float",
    "avg_duration_days": "float (calcolato)",
    "automation_level": "enum: manual | semi-auto | full-auto",
    "cost_per_execution": "float (EUR)",
    "frequency":       "enum: realtime | daily | weekly | monthly | adhoc",
    "bpmn_ref":        "string (URL al modello BPMN)"
  }
}
```

### KPI
Indicatore chiave di performance.

```json
{
  "type": "KPI",
  "required": ["id", "name", "unit", "owner_id"],
  "properties": {
    "id":                "string (UUID)",
    "name":              "string",
    "description":       "string",
    "unit":              "string (%, EUR, count, days, ratio...)",
    "owner_id":          "string (FK → OrganizationUnit or Person)",
    "polarity":          "enum: higher_better | lower_better",
    "target":            "float",
    "warning_threshold": "float",
    "critical_threshold":"float",
    "formula":           "string (espressione calcolata)",
    "data_source":       "string (ERP, CRM, manual...)",
    "update_frequency":  "enum: realtime | hourly | daily | weekly | monthly"
  }
}
```

### ITSystem
Sistema informatico aziendale.

```json
{
  "type": "ITSystem",
  "required": ["id", "name", "category"],
  "properties": {
    "id":         "string (UUID)",
    "name":       "string",
    "category":   "enum: ERP | CRM | HRMS | BPM | BI | custom | cloud",
    "vendor":     "string",
    "version":    "string",
    "api_url":    "string",
    "is_cloud":   "boolean",
    "criticality":"enum: low | medium | high | critical"
  }
}
```

---

## Relazioni (Edge Types)

| Relazione | Da | A | Proprietà |
|-----------|-----|-----|-----------|
| `BELONGS_TO` | Person | OrganizationUnit | `since_date`, `fte` |
| `REPORTS_TO` | Person | Person | `since_date` |
| `MANAGES` | Person | OrganizationUnit | `since_date`, `is_interim` |
| `HAS_ROLE` | Person | Role | `since_date`, `appointment_type` |
| `PART_OF` | OrganizationUnit | OrganizationUnit | `since_date` |
| `OWNS_PROCESS` | OrganizationUnit | Process | `since_date`, `ownership_type` |
| `EXECUTES_PROCESS` | Person | Process | `avg_time_days`, `completions` |
| `DEPENDS_ON` | Process | Process | `dependency_type`, `is_blocking` |
| `MEASURED_BY` | Process | KPI | `measurement_type` |
| `MEASURED_BY` | OrganizationUnit | KPI | `aggregation: sum/avg` |
| `USES_SYSTEM` | Process | ITSystem | `integration_type` |
| `SUPPORTED_BY` | OrganizationUnit | ITSystem | `criticality` |

---

## Cypher Queries Fondamentali

### Struttura organizzativa completa
```cypher
MATCH path = (org:Organization)-[:PART_OF*0..5]-(unit:OrganizationUnit)
RETURN path
```

### Catena di reporting
```cypher
MATCH chain = (emp:Person {id: $employee_id})-[:REPORTS_TO*1..6]->(ceo:Person)
WHERE NOT (ceo)-[:REPORTS_TO]->()
RETURN [node IN nodes(chain) | node.employee_id] AS reporting_chain
```

### Processi ad alto rischio (SLA violation + manual)
```cypher
MATCH (p:Process)
WHERE p.avg_duration_days > p.sla_days
  AND p.automation_level = 'manual'
RETURN p.name, p.owner_unit_id,
       p.avg_duration_days - p.sla_days AS sla_gap_days,
       p.cost_per_execution AS cost
ORDER BY sla_gap_days DESC
```

### KPI a rischio (valori vicini alla soglia critica)
```cypher
MATCH (k:KPI)
WHERE k.polarity = 'higher_better'
  AND k.current_value < k.warning_threshold
RETURN k.name, k.current_value, k.warning_threshold,
       k.critical_threshold, k.owner_id
```

### Dipendenze circolari tra processi
```cypher
MATCH cycle = (p:Process)-[:DEPENDS_ON*2..10]->(p)
RETURN [node IN nodes(cycle) | node.name] AS cycle_nodes
```
