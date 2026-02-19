# DTO Sensore Temperatura 🌡️

Questo progetto è un esempio di **Digital Twin of an Organization (DTO)** applicato a un sensore IoT. Utilizza un'architettura modulare per simulare, monitorare e prevedere il comportamento di un sensore di temperatura.

## Caratteristiche
- **Simulatore Sensore**: Genera dati realistici con variazioni cicliche diurne, rumore e anomalie casuali.
- **DTO Engine**: 
    - **Anomaly Detection**: Utilizza `IsolationForest` di scikit-learn per rilevare letture fuori norma.
    - **Trend Prediction**: Utilizza `LinearRegression` per prevedere l'andamento futuro.
- **Real-time Dashboard**: Sincronizzazione dati tramite Socket.IO e visualizzazione dinamica.
- **Visualizzazione Scientifica**: Grafici generati con `Matplotlib` direttamente nel backend.

## Requisiti
- Python 3.10+ o Docker

## Come Eseguire (Locale)
1. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
2. Avvia l'app:
   ```bash
   python app/main.py
   ```
3. Vai su `http://localhost:5000`

## Come Eseguire (Docker)
1. Avvia i container:
   ```bash
   docker-compose up --build
   ```
2. Vai su `http://localhost:5000`

## Struttura del Progetto
- `app/`: Backend Flask e Socket.IO.
- `core/`: Motore del Digital Twin (ML e Logica).
- `templates/`: Interfaccia Utente.
- `static/`: Asset statici.
- `simulation/`: Thread di simulazione sensore.

---
Creato nell'ambito del progetto **Digital Twin Factory**.
