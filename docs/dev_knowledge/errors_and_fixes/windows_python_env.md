# 🪟 Knowledge Item: Ambiente Windows & Python Path

**Data**: 2026-02-19  
**Categoria**: Ambiente di Sviluppo  
**Ambito**: Windows PowerShell

---

## ❌ Problema 1: `pip` non trovato
L'utente o l'AI tenta di eseguire `pip install`, ma il comando fallisce perché non è nel PATH globale o l'alias non è configurato.

### ✅ Soluzione:
Usa il modulo python direttamente o punta al path specifico del venv:
```powershell
# Opzione A (Usa il venv specifico)
c:/Users/Lorenzo/Desktop/Fabbrica_dei_digitalTwin/.venv/Scripts/python.exe -m pip install -r requirements.txt

# Opzione B (Alias py)
py -m pip install -r requirements.txt
```

---

## ❌ Problema 2: `ModuleNotFoundError: No module named 'core'`
Eseguendo uno script da una sottocartella (es. `app/main.py`), Python non vede la cartella `core` che si trova al livello superiore (root del progetto).

### ✅ Soluzione:
Configura la variabile d'ambiente `PYTHONPATH` prima dell'esecuzione per includere la root:
```powershell
# PowerShell: Imposta per la sessione corrente
$env:PYTHONPATH="."

# PowerShell: Esecuzione inline (percorso venv specifico)
$env:PYTHONPATH="."; c:/Users/Lorenzo/Desktop/Fabbrica_dei_digitalTwin/.venv/Scripts/python.exe app/main.py
```
*⚠️ **Critico**: Assicurarsi che le cartelle (es. `core/`, `app/`) contengano un file `__init__.py` (anche vuoto). Senza di esso, Python potrebbe non riconoscere la struttura dei package in ambienti Windows con configurazioni di esecuzione specifiche.*

---

## ❌ Problema 3: Browser Tool failure ($HOME non set)
Il tool `open_browser_url` fallisce con errore `failed to install playwright: $HOME environment variable is not set`.

### ✅ Soluzione (Workaround):
Non è possibile risolvere via software se l'ambiente host è restrittivo. 
**Verifica alternativa:** Usa `Invoke-WebRequest` in PowerShell per testare se il server Flask è attivo.

```powershell
# Test semplice
Invoke-WebRequest -Uri http://127.0.0.1:5000 -UseBasicParsing

# Verifica rapida dello stato e del contenuto (per vedere se serve il file corretto)
Invoke-WebRequest -Uri http://127.0.0.1:5000 -UseBasicParsing | Select-Object -ExpandProperty Content | Select-String "Dinamico"
```

---

## 💡 Best Practice per l'esecuzione del DTO
Per avviare correttamente il progetto "DTO Sensore Temperatura" su questa macchina:
1. Naviga in `DTO Sensore Temperatura/`.
2. Esegui: `$env:PYTHONPATH="."; c:/Users/Lorenzo/Desktop/Fabbrica_dei_digitalTwin/.venv/Scripts/python.exe app/main.py`.
