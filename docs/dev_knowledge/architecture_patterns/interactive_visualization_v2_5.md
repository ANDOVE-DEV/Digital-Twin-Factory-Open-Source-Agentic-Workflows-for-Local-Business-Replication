# 📊 Knowledge Item: Interactive Visualization (V2.5)

**Data**: 2026-02-19  
**Categoria**: Frontend & UX  
**Status**: Migrato a Chart.js

---

## 🎨 Evoluzione del Grafico
Abbiamo rimosso la generazione dei grafici PNG lato server (Matplotlib) a favore di un rendering dinamico lato client utilizzando **Chart.js**.

### Motivazioni della scelta:
1.  **Interattività**: L'utente può passare il mouse sopra i singoli punti per leggere i valori esatti (fondamentale per "capire" i dati).
2.  **Prestazioni**: Ridotto il carico sulla CPU del server e rimosse le dipendenze da librerie GUI (Tkinter) che causavano crash in ambienti multi-threaded.
3.  **Estetica Premium**: Utilizzo di gradienti di colore, curve Cubic Spline (tension 0.4) e animazioni fluide.

---

## 🛠️ Stack Tecnologic
- **Frontend**: Chart.js 4.x via CDN.
- **Dati**: Socket.IO stream invia un JSON strutturato con:
  - `temperature`: Dato live attuale.
  - `sma`: Media mobile calcolata dal DTO Engine.
  - `predictions`: Array di 8 punti futuri calcolati tramite Linear Regression.

---

## 🔬 Dettagli Tecnici Implementation
- **Sliding Window**: Il grafico mantiene solo gli ultimi 30 punti per garantire fluidità.
- **Prediction Overlay**: Le predizioni ML vengono visualizzate come una linea tratteggiata che parte dall'ultimo punto reale, distinguendo chiaramente tra "Presente" e "Futuro Analitico".
