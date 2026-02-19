# BPA ↔ DTO Integration
## Riferimento al documento completo di integrazione

Questo file rimanda al documento master dell'integrazione bidirezionale
tra **BPA** (Business Process Automation) e **DTO** (Digital Twin of an Organization).

---

> 📄 **Documento completo:**  
> `.agent/skills/skills/dto-digital-twin-organization/resources/dto-bpa-integration.md`

Il documento master contiene:

1. **Filosofia dell'integrazione** — il modello OODA e il loop chiuso Sense→Decide→Act→Measure
2. **Contratto degli eventi** — `IntegrationEvent` schema condiviso con `EventDirection` e `EventPriority`
3. **Catalogo eventi completo** — tutti gli eventi DTO→BPA e BPA→DTO con descrizione e mapping workflow
4. **Event Bus implementation** — codice Python per Redis Streams (publisher + consumer + ACK)
5. **DTO Publisher** — come il twin pubblica eventi verso il BPA (`DTOEventPublisher`)
6. **BPA Consumer & Dispatcher** — come il BPA riceve eventi e avvia workflow (`BPAEventConsumer`)
7. **DTO Updater** — come il BPA aggiorna il twin dopo ogni esecuzione (`DTOUpdater`)
8. **DTO Consumer** — come il twin riceve aggiornamenti dal BPA (`DTOEventConsumer`)
9. **Sequenze End-to-End** — diagrammi di flusso per scenari reali (SLA breach, offboarding)
10. **Setup rapido** — bootstrap completo con `asyncio.gather`
11. **Configurazione YAML** — `config/integration.yaml` con tutti i parametri

---

## Posizione del BPA nel Loop

```
┌──────────────────────────────────────────────────────────────┐
│                   FABBRICA DEI DIGITAL TWIN                  │
│                                                              │
│   [DTO — Sense & Model]  ──events──►  [BPA — Act & Execute] │
│          ▲                                      │            │
│          └────────── KPI updates ───────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

Il **BPA** è il braccio esecutivo:
- **Consuma** eventi `dto.kpi.anomaly_detected`, `dto.process.sla_breach`, `dto.org.vacancy_detected`, `dto.budget.overrun_predicted`, `dto.vendor.risk_elevated`, `dto.compliance.deadline_approaching`
- **Pubblica** aggiornamenti `bpa.workflow.completed`, `bpa.employee.onboarded`, `bpa.process.automated`, `bpa.sla.resolved`, `bpa.kpi.updated`

---

## Quick Reference: Evento → Workflow

| Evento DTO ricevuto | Workflow BPA avviato |
|---------------------|---------------------|
| `dto.kpi.anomaly_detected` (CRITICAL) | `kpi-anomaly-response` |
| `dto.kpi.anomaly_detected` (HIGH) | `kpi-anomaly-response` |
| `dto.process.sla_breach` (CRITICAL) | `sla-critical-escalation` |
| `dto.process.sla_breach` (HIGH) | `sla-escalation-workflow` |
| `dto.org.vacancy_detected` | `hiring-request-workflow` |
| `dto.budget.overrun_predicted` | `budget-alert-workflow` |
| `dto.vendor.risk_elevated` | `vendor-review-workflow` |
| `dto.compliance.deadline_approaching` | `compliance-check-workflow` |
