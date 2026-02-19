# 🏗️ Knowledge Item: Closed Loop AI Learning Architecture

**Data**: 2026-02-19  
**Categoria**: Architettura AI  
**Relazione**: Integrato con DTO & BPA

---

## 🧭 Visione
La "Fabbrica dei Digital Twin" non è solo produttiva ma anche **auto-evolutiva**. Il sistema deve imparare non solo dai dati dei sensori (DTO), ma anche dai dati del proprio processo di sviluppo.

---

## 🛠️ Il Pattern "Meta-Twin"
Oltre al Digital Twin del business (DTO), questo repository implementa un "Meta-Twin" del software stesso tramite la Knowledge Base dinamica in `docs/dev_knowledge/`.

### Componenti del Loop:
1.  **Repository di Conoscenza (`docs/dev_knowledge/`)**: Lo "Stato" della conoscenza del sistema.
2.  **Protocollo di Ricerca**: Obbligo di controllare la KB come primo step di ogni task.
3.  **Protocollo di Aggiornamento**: Obbligo di caricare ogni nuova "lezione appresa" nel sistema.

### Vantaggi:
- **Resilienza**: L'AI non dimentica come risolvere errori di configurazione tra diverse sessioni.
- **Scalabilità**: Nuovi agenti possono leggere la KB e diventare immediatamente operativi con lo stack specifico dell'utente.
- **Evoluzione**: Il sistema diventa "più intelligente" quanto più viene usato.

---

## 📋 Regola d'Oro per gli Agenti
> "Un'azione fallita è un errore. Un'azione fallita che non viene documentata nella KB è un fallimento del sistema."

In caso di errore bloccante, l'agente deve:
1. Documentare l'errore.
2. Documentare i tentativi falliti.
3. Documentare la soluzione (o il motivo per cui non è risolvibile al momento).
