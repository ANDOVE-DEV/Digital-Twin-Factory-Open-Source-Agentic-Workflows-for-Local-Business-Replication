---
name: twin-architect
description: Guides the user through defining requirements for a new Digital Twin.
tags: [factory, requirements, architect]
---

# Twin Architect

## Goal
To understand what kind of Digital Twin the user needs and design its architecture.

## Workflow

### 1. Discovery
Ask the user:
- **Purpose**: What job will this Twin do?
- **Trigger**: What event starts the work?
- **Data**: What documents or systems are involved?
- **Output**: What is the result?

### 2. Matching
Identify which factory template fits best:
- `bpa-base` (General purpose)
- `bpa-finance` (Invoice/Expense heavy)
- `bpa-email` (Communication heavy)

### 3. Blueprinting
Create a plan file `TWIN_PLAN.md` with:
- Twin Name
- List of Required Skills (from Catalog)
- Integration Points
