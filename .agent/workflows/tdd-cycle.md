---
description: Ciclo TDD per sviluppo feature
---

# TDD Cycle Workflow

Segui questo flusso per ogni nuova feature o fix.

## Steps

1. **Leggi la specifica**
   - Apri `.agent/spec.md` e identifica il task da implementare.

2. **Crea il branch feature**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nome-task
   ```

3. **Scrivi il test FIRST**
   - Crea il file di test (es. `tests/test_nome_task.py` o `__tests__/nomeTask.test.ts`).
   - Il test DEVE fallire inizialmente.

4. **Implementa il codice**
   - Scrivi il codice minimo per far passare il test.

5. **Esegui i test**
   ```bash
   # Python
   pytest tests/

   # Node.js
   npm test
   ```

6. **Commit atomico (solo se test passano)**
   // turbo
   ```bash
   git add .
   git commit -m "feat(nome-task): descrizione breve"
   ```

7. **Merge in develop**
   ```bash
   git checkout develop
   git merge feature/nome-task --no-ff
   git branch -d feature/nome-task
   ```

## Safety Rules
- ❌ Mai fare commit se i test falliscono
- ❌ Mai saltare la creazione del test
- ✅ Sempre eseguire la suite completa prima del merge
