# 🌡️ Knowledge Item: Closed-Loop Temperature Control (V2)

**Data**: 2026-02-19  
**Categoria**: Implementazione DTO/BPA  
**Status**: Versione 2.0 (Migliorata)

---

## 📈 Nuove Funzionalità Implementate

### 1. Persistenza dei Dati (SQLite)
Il DTO non perde più la memoria allo spegnimento. 
- **DB Path**: `DTO Sensore Temperatura/dto_storage.db`
- **Tabella**: `readings` (id, timestamp, temperature, is_anomaly)
- **Vantaggio**: Consente analisi storiche a lungo termine e ricostruzione di trend post-riavvio.

### 2. Feedback Loop (Closed-Loop)
Il BPA non si limita a loggare l'errore, ma "agisce" sul Digital Twin:
- Se `temp > 28°C` → Il BPA applica un `delta -2.0` alla simulazione.
- Se `temp < 15°C` → Il BPA applica un `delta +2.0`.
- **Meccanismo**: L'influenza decade gradualmente del 5% ad ogni ciclo per simulare il ritorno all'equilibrio termico naturale.

### 3. Analisi Avanzata nel DTO Engine
- **SMA (Simple Moving Average)**: Calcolo in tempo reale della media mobile a 10 campioni per filtrare il rumore del sensore.
- **ML Integration**: `IsolationForest` aggiorna il training dinamicamente man mano che arrivano nuovi dati dal DB.

---

## 🎨 Dashboard UI V2 (Aesthetics)
- **Design**: Glassmorphism con palette Neon Blue / Deep Space.
- **Visual**: Integrazione della media mobile (SMA) nel grafico Matplotlib.
- **Feedback**: Console di log in tempo reale che distingue tra eventi di sistema (INIT), eventi AI (ALARM) e azioni BPA.

---

## 🛠️ Note Tecniche per l'Esecuzione
Per avviare la V2:
```powershell
$env:PYTHONPATH="."; c:/Users/Lorenzo/Desktop/Fabbrica_dei_digitalTwin/.venv/Scripts/python.exe app/main.py
```
*Assicurarsi che la root `DTO Sensore Temperatura/` contenga `dto_storage.db` dopo il primo avvio.*
