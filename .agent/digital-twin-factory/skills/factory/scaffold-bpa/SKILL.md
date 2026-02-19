---
name: scaffold-bpa
description: Generates the folder structure for a new Digital Twin based on templates.
tags: [factory, generator, scaffold]
---

# Scaffold BPA

## Goal
To physically create the directory and files for a new Digital Twin.

## Usage
1. Identify the target template (e.g., `templates/bpa-base`).
2. Identify the target name (e.g., `invoice-bot`).
3. Copy the template to `twins/<target-name>`.
4. Customize `TWIN_INSTRUCTIONS.md` with the specific rules gathered during architecture.
5. Create a `bootstrap.py` for the new Twin.

## Structure to Generate
```text
twins/
  <twin-name>/
    .agent/ (Empty, ready for bootstrap)
    knowledge/ (For user docs)
    tasks/ (For task tracking)
    TWIN_INSTRUCTIONS.md
    bootstrap.py
```
