# 📉 Knowledge Item: Crash Matplotlib (Tkinter) su Windows

**Data**: 2026-02-19  
**Categoria**: Stabilità & Threading  
**Ambito**: Python / Flask / Windows

---

## ❌ Problema: `RuntimeError: main thread is not in main loop`
Durante l'esecuzione del Digital Twin con Flask e Socket.IO, il sistema crashava sistematicamente dopo pochi secondi di simulazione.

### Causa Radical:
- **Matplotlib** su Windows utilizza di default il backend `TkAgg`.
- `Tkinter` (su cui si poggia TkAgg) **non è thread-safe**.
- Flask/Socket.IO eseguono il server e i thread di simulazione in contesti diversi. Quando il thread di simulazione tentava di generare un plot tramite Matplotlib, Tkinter lanciava l'errore perché l'operazione non avveniva nel thread principale (main thread).

---

## ✅ Soluzione Definitiva: Offloading al Client
Sebbene esistano workaround (es. usare il backend `Agg` non interattivo), la soluzione più scalabile e performante per un Digital Twin è stata:

1. **Rimuovere Matplotlib dal Backend**: Eliminata la generazione di immagini PNG sul server.
2. **Streaming di Dati Raw**: Il server invia ora solo piccoli oggetti JSON contenenti i valori numerici.
3. **Rendering Client-Side (Chart.js)**: Il browser dell'utente si occupa di disegnare il grafico.

### Vantaggi:
- **Zero Crash**: Nessun conflitto di thread sul server.
- **Interattività**: Il grafico ora supporta zoom, tooltip e hover (impossibile con il PNG statico).
- **Efficienza**: Ridotta drasticamente l'occupazione di memoria e CPU sul server.

---

## 💡 Lezione Appresa
> "Per dashboard real-time basate su web, non generare mai grafici come immagini sul server. Usa sempre librerie JS interattive (Chart.js, D3.js, Plotly) alimentate da stream di dati via WebSocket."
