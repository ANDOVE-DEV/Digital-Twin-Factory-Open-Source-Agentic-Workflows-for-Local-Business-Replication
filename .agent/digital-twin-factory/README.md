# 🏭 Digital Twin Factory

**The Agent that builds Agents.**

This repository is not a standard codebase. It is a **Meta-Agent Environment** designed to turn your AI Assistant (Claude, Gemini, etc.) into a specialized **Digital Twin Architect**.

## 🚀 Vision

Instead of manually coding every automation, you use this Factory to **generate** specialized "Digital Twins" for your business processes.

-   **Input**: "I need a twin to handle invoice approvals."
-   **Factory**: Designs the architecture, selects the skills, and scaffolds the code.
-   **Output**: A fully configured `invoice-approval-twin` agent ready to run.

## 🛠️ Installation

1.  **Clone this repository**:
    ```bash
    git clone https://github.com/your-username/digital-twin-factory.git
    cd digital-twin-factory
    ```

2.  **Bootstrap the Factory**:
    ```bash
    python bootstrap.py
    ```
    This sets up the environment and downloads the latest factory skills.

3.  **Activate**:
    Open this folder in your IDE (VS Code, Cursor, Windsurf).
    Tell your AI Assistant:
    > "You are the Factory. Read `FACTORY_INSTRUCTIONS.md` and await my command."

## 🧩 How it Works

The Factory operates on three layers:
1.  **Meta-Skills (`skills/factory/`)**: Capabilities that teach the AI how to interview users and scaffold projects.
2.  **Blueprints (`templates/`)**: Pre-built architectures for common patterns (e.g., Document Processing, Email Triage).
3.  **The Catalog (`CATALOG.md`)**: A searchable index of all available skills the Factory can deploy to its Twins.

## 🏗️ Usage Example

**User**: "I want to create a new Digital Twin for HR Candidate Screening."

**Factory (AI)**: "Understood. I'll use the `twin-architect` skill. First, tell me: what is the trigger for this process (e.g., email, application form)?"

*(Conversation continues...)*

**Factory (AI)**: "Design complete. I am now scaffolding `twins/hr-screener` using the `bpa-base` template."

## 🤝 Contributing

Add new "Factory Skills" to `skills/factory/` to teach the Architect new tricks.
Add new "Blueprints" to `templates/` to provide better starting points.
