# 🧠 Dynamic Knowledge Base (Self-Learning Protocol)

Questa cartella contiene la memoria tecnica del progetto. Ogni volta che viene risolto un problema o implementata una nuova feature, l'AI deve consultare, arricchire e aggiornare questa Knowledge Base.

---

## 🔄 Il Ciclo di Apprendimento Continuo

Ogni volta che ricevi un task, segui rigorosamente queste 3 fasi:

### 1. 🔍 Phase 1: RESEARCH (Controllo)
*Prima di scrivere codice o eseguire comandi:*
- Cerca in `docs/dev_knowledge/` se esistono soluzioni a problemi simili.
- Verifica i "Gotchas" tecnici già documentati per evitare di ripetere errori passati (es. comandi Windows specifici, configurazioni environment).

### 2. 🛠️ Phase 2: RESOLUTION (Esecuzione)
*Risolvi il problema tecnico:*
- Applica la soluzione trovata o sviluppane una nuova.
- Se la soluzione esistente era errata o incompleta, prendi nota della correzione.

### 3. ✍️ Phase 3: UPDATE (Aggiornamento)
*Consolida la conoscenza:*
- Se hai imparato qualcosa di nuovo (un errore risolto, un pattern efficace), aggiorna il file `.md` corrispondente o creane uno nuovo.
- Formatta i nuovi contenuti in modo che siano facilmente "digeribili" dall'AI nelle sessioni successive.

---

## 📂 Organizzazione della KB

- `/errors_and_fixes/`: Soluzioni a bug specifici e configurazioni dell'ambiente.
- `/architecture_patterns/`: Decisioni di design e best practices per DTO e BPA.
- `/workflow_templates/`: Snippet pronti per automazioni frequenti.

---

## 📜 Registro Aggiornamenti KB
| Data | Argomento | Tipo |
|------|-----------|------|
| 2026-02-19 | Inizializzazione KB | Struttura |
| 2026-02-19 | [Ambiente Windows & Python Path](./errors_and_fixes/windows_python_env.md) | Bugfix |
| 2026-02-19 | [Crash Matplotlib (Tkinter)](./errors_and_fixes/visualization_crashes.md) | Bugfix |
| 2026-02-19 | [Closed Loop V2 & Persistence](./architecture_patterns/closed_loop_v2_implementation.md) | Architettura |
| 2026-02-19 | [Interattività Chart.js](./architecture_patterns/interactive_visualization_v2_5.md) | UX/UI |

---

## 📅 Diario Sessione (19 Febbraio 2026)

### Stato Iniziale:
- Repository configurata con skill DTO/BPA di base.
- Primo progetto: DTO Sensore Temperatura (V1 statica).

### Problemi Rilevati:
1. **Ambiente**: Difficoltà di esecuzione comandi Python (`pip`, `python`) direttamente nel terminale Windows dell'utente.
2. **Architettura**: Problema di visibilità moduli (`core`) durante l'esecuzione da cartelle annidate.
3. **Stabilità**: Crash fatale su Windows (`RuntimeError: main thread is not in main loop`) causato dall'uso di Matplotlib in un thread secondario all'interno di Flask.
4. **Strumenti**: Il tool `open_browser_url` dell'agente è risultato inaccessibile per via di configurazioni host.

### Soluzioni Applicate:
- Implementato l'uso di `PYTHONPATH="."` e path assoluti del venv.
- Migrazione totale da **Matplotlib** (server-side) a **Chart.js** (client-side interattivo).
- Re-factoring del DTO per includere persistenza **SQLite** (evitando perdite dati al crash).
- Metodo di verifica server tramite `Invoke-WebRequest`.
