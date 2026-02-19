---
description: Creare e gestire feature branch
---

# Feature Branch Workflow

Workflow per la gestione dei branch secondo Git Flow semplificato.

## Creare un nuovo feature branch

// turbo
```bash
git checkout develop
git pull origin develop
git checkout -b feature/{nome-task}
```

## Lavorare sul feature branch

1. Implementa le modifiche seguendo il workflow TDD (`/tdd-cycle`).
2. Fai commit atomici frequenti.

## Merge in develop

Prima di fare merge, esegui TUTTI i test:

```bash
# Python
pytest

# Node.js
npm test
```

Solo se i test passano:

// turbo
```bash
git checkout develop
git merge feature/{nome-task} --no-ff -m "Merge feature/{nome-task}"
git branch -d feature/{nome-task}
```

## Release (da develop a main)

Quando la specifica è completa al 100%:

```bash
git checkout main
git merge develop --no-ff -m "Release vX.Y.Z"
git tag -a vX.Y.Z -m "Release stabile: descrizione"
git push origin main --tags
```

## Regole Sacchi
- **Safety-first**: Mai lavorare su `main` direttamente.
- **Little-often**: Commit frequenti e atomici.
- **Double-check**: Test sempre prima del merge.
