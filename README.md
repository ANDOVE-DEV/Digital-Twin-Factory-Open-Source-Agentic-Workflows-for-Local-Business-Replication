# Digital Twin Factory 🏭
## Open Source Agentic Workflows for Local Business Replication

Benvenuti nella **Digital Twin Factory**, una suite avanzata di architetture AI progettata per creare gemelli digitali di organizzazioni (DTO) e automatizzare i processi aziendali (BPA) in modo modulare e scalabile.

Questo repository contiene le specifiche tecniche, i playbook di implementazione e gli schemi ontologici per costruire una "fabbrica" di Digital Twin basata su agenti AI.

---

## 📂 Struttura del Repository

Il progetto è diviso in due skill fondamentali e interconnesse:

### 🏭 [dto-digital-twin-organization](./skills/dto-digital-twin-organization)
*L'Organo di Senso e Modellazione*
- **Semplificazione**: Crea una copia digitale dell'azienda.
- **Funzioni**: Modella strutture, processi e KPI. Rileva anomalie e simula scenari "what-if".
- **Playbook**: Architettura 4-layer, Grafo Neo4j, Intelligence con LLM RAG.

### ⚙️ [bpa-business-process-automation](./skills/bpa-business-process-automation)
*L'Organo Esecutivo e di Ottimizzazione*
- **Semplificazione**: Automatizza le azioni basandosi sugli insight del twin.
- **Funzioni**: Orchestrazione workflow intelligenti, integrazione RPA, agenti AI decisionali.
- **Playbook**: Workflow Temporal/n8n, Agent LangChain, Catalogo di 20 processi pronti all'uso.

---

## 🏗️ Progetti Demo Live
Esempi pratici di implementazione Sense-Think-Act inclusi in questo repository:

1. **[DTO Sensore Temperatura](./DTO%20Sensore%20Temperatura)**: 
   - Monitoraggio real-time con regressione lineare per predizioni ML.
   - Closed-loop con BPA per gestione anomalie termiche.
   - Dashboard interattiva in Chart.js.

2. **[OpenFactoryTwin](./OpenFactoryTwin)**:
   - Simulazione di una mini-fabbrica con 3 macchine.
   - Ottimizzazione energetica guidata da n8n.

3. **[GreenAI PlantTwin](./GreenAI_PlantTwin)**:
   - Bio-Twin High-Fidelity con modellazione 3D (Three.js).
   - Simulazione complessa: evapotraspirazione, nutrienti e umidità.
   - Dashboard professionale in Glassmorphism e automazione n8n.

---

## 🔗 Integrazione Sense-Decide-Act

Le due skill lavorano in un loop chiuso (Closed-Loop Management):
1. **DTO** rileva un'anomalia o una necessità (es. violazione SLA).
2. **DTO** pubblica un evento sul bus dedicato.
3. **BPA** riceve l'evento e avvia il workflow di risposta automatica.
4. **BPA** aggiorna lo stato dei KPI nel **DTO** a esecuzione completata.

Per i dettagli tecnici dell'integrazione, consulta il documento:  
[`dto-bpa-integration.md`](./skills/dto-digital-twin-organization/resources/dto-bpa-integration.md)

---

## 🚀 Come Iniziare (Setup Locale)

La repository include un ambiente Docker pronto all'uso che istanzia l'infrastruttura di base (Database a Grafo, Motore Workflow, Event Bus, Motore DTO). È il modo più veloce per testare l'integrazione DTO ↔ BPA nella tua macchina.

### Prerequisiti
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose installati.

### Avvio della Fabbrica Locale
1. Clona la repository ed entra nella cartella principale:
   ```bash
   git clone https://github.com/tuo-user/Digital-Twin-Factory.git
   cd Digital-Twin-Factory
   ```
2. Avvia i servizi in background:
   ```bash
   docker compose up -d
   ```
3. Verifica i servizi attivi:
   - **n8n (BPA Workflow Engine)**: http://localhost:5678
   - **Neo4j (DTO Graph Model Layer)**: http://localhost:7474 (user: `neo4j`, pass: `dtf-secret-password`)
   - **FastAPI (DTO Core Engine Base)**: http://localhost:8000
   - **Redis (Event Bus)**: in ascolto sulla porta `6379` interne al network Docker.

Una volta accesa l'infrastruttura, puoi iniziare a sviluppare la logica del tuo gemello digitale modificando il file `core_engine/main.py`.

---

## 📚 Esplorazione e Guide

Se desideri studiare la teoria o lanciare le singole demo standalone (senza l'infrastruttura Docker globale descritta sopra):

1. Esplora le cartelle nella directory `skills/` per comprendere i ruoli degli agenti.
2. Consulta i **Playbook** nelle sottocartelle `resources/` per esempi di codice e guide passo-passo.
3. Segui la **Checklist di Implementazione** fornita in ogni playbook.

---

## 🛠️ Stack Tecnologico Consigliato

- **Graph DB**: Neo4j / Azure Digital Twins
- **Workflow Engine**: Temporal.io / n8n
- **Intelligence**: LangChain, OpenAI, OpenRouter
- **Event Bus**: Redis Streams / Apache Kafka
- **API Framework**: FastAPI (Python)

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza Open Source. Sentiti libero di contribuire e adattarlo alle tue esigenze locali.

---
*Building the future of autonomous organizations.*
