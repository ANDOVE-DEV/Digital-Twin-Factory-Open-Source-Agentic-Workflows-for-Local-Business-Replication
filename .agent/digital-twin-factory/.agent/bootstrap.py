#!/usr/bin/env python3
"""
Digital Twin Factory Bootstrap Script
=====================================
Configures the environment for the Digital Twin Factory.
This script initializes the 'Factory' agent capabilities by setting up the .agent environment.

Usage: python .agent/bootstrap.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent  # Repository root
AGENT_DIR = Path(__file__).parent         # .agent directory
SKILLS_DIR = AGENT_DIR / "skills"
VENV_DIR = AGENT_DIR / ".venv"

# TODO: Replace with your own skills repository if you have custom factory skills
SKILLS_REPO = "https://github.com/sickn33/antigravity-awesome-skills.git"

def run_command(command, check=True, cwd=None, capture=True):
    """Run a shell command and return result."""
    print(f"  -> {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=check,
            cwd=cwd or BASE_DIR,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
        if capture and result.stdout and result.stdout.strip():
            print(f"    {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"  [X] Error: {e}")
        if e.stderr:
            print(f"    {e.stderr.strip()}")
        if check:
            sys.exit(1)
        return e

def check_dependencies():
    """Check for required tools."""
    print("\n=== 1. CHECKING FACTORY TOOLS ===")
    
    # Node.js
    print("- Node.js (Required for Factory processing)...")
    node_res = run_command(["node", "--version"], check=False)
    if node_res.returncode != 0:
        print("  [!] Node.js not found. Install via https://nodejs.org/")
    else:
        print(f"  [OK] Node.js {node_res.stdout.strip()}")

    # Git
    print("- Git...")
    git_res = run_command(["git", "--version"], check=False)
    if git_res.returncode != 0:
        print("  [X] Git not found. Please install Git.")
        sys.exit(1)
    print(f"  [OK] {git_res.stdout.strip()}")
    
    # Python
    print(f"- Python {sys.version.split()[0]}")
    print("  [OK]")

def setup_venv():
    """Setup Python virtual environment in .agent/.venv."""
    print("\n=== 2. FACTORY ENVIRONMENT (Python) ===")
    
    if not VENV_DIR.exists():
        print(f"- Creating venv in {VENV_DIR}...")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("  [OK] Factory environment created")
    else:
        print(f"  [OK] venv already exists at {VENV_DIR}")

def setup_skills():
    """Clone Factory Skills into .agent/skills."""
    print("\n=== 3. ACQUIRING FACTORY SKILLS ===")
    
    if not SKILLS_DIR.exists():
        print(f"- Cloning skills to {SKILLS_DIR}...")
        run_command(["git", "clone", SKILLS_REPO, str(SKILLS_DIR)])
        print("  [OK] Factory skills acquired")
    else:
        print(f"  [OK] Skills directory exists")
        print("- Pulling latest updates...")
        run_command(["git", "pull"], cwd=SKILLS_DIR, check=False)

def print_summary():
    """Print final summary and next steps."""
    print("\n" + "=" * 50)
    print("        [OK] DIGITAL TWIN FACTORY READY!")
    print("=" * 50)
    print("""
Your Digital Twin Factory is initialized.

Structure:
  .agent/              (Factory Brain)
  |-- skills/          (Meta-skills for building twins)
  templates/           (Blueprints for new twins)
  FACTORY_INSTRUCTIONS.md (The Architect's Persona)

Next Steps:
  1. Open this folder in your IDE with your AI Assistant.
  2. Tell the AI: "You are the Factory. Read FACTORY_INSTRUCTIONS.md and help me build a Twin."
  3. Example prompt: "I need a Digital Twin for processing Vendor Invoices."
""")

def main():
    print("=" * 50)
    print("   DIGITAL TWIN FACTORY BOOTSTRAP")
    print("   Initializing Agentic Architecture")
    print("=" * 50)
    
    check_dependencies()
    setup_venv()
    setup_skills()
    print_summary()

if __name__ == "__main__":
    main()
