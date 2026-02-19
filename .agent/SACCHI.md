# Metodologia Sacchi per Sviluppo Agentico

## Filosofia

La metodologia **Sacchi** guida lo sviluppo agentico con tre principi fondamentali:

| Principio | Descrizione | Applicazione |
|-----------|-------------|--------------|
| **Safety-first** | Mai lavorare direttamente su `main`. Isolamento totale. | Ogni agente lavora in branch feature isolati. Venv separati. |
| **Little-often** | Commit atomici e frequenti. | Ogni test passato = 1 commit. Nessun commit massivo. |
| **Double-check** | Validazione obbligatoria prima di merge. | Suite di test eseguita prima di ogni merge in `develop`. |

---

## Git Flow Semplificato

```
main ────────────────────────────────● tag v1.0.0
                                    ╱
develop ──●────●────●────●────●────●
          ╲   ╱    ╲   ╱    ╲   ╱
feature/1  ●─●      │   │      │
                    │   │      │
feature/2           ●───●      │
                               │
feature/3                      ●───●
```

### Branch Rules
- **main**: Solo merge da `develop` con tag. Immutabile.
- **develop**: Integrazione continua. Target per merge.
- **feature/nome-task**: Branch per singoli task. Effimeri.

---

## Ciclo di Sviluppo (TDD)

```
1. Leggi spec.md (Source of Truth)
2. Crea branch feature/nome-task
3. Scrivi test FIRST (fallimentare)
4. Implementa codice
5. Esegui test
   └── FAIL → Torna a step 4
   └── PASS → Commit atomico
6. Merge in develop (dopo Double-check)
7. Elimina feature branch
```

---

## Checklist Prima di Commit

- [ ] Test eseguiti e passati
- [ ] Nessun file `.env` nel commit
- [ ] Codice revisionato (se possibile)
- [ ] Commit message descrittivo

## Checklist Prima di Merge

- [ ] Tutti i test della suite passano
- [ ] Branch aggiornato con develop
- [ ] Review completata (se richiesta)
