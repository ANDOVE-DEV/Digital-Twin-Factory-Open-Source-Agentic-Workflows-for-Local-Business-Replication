#!/usr/bin/env python3
"""
Agentic Environment Bootstrap Script
=====================================
Configures the complete agentic development environment following Sacchi methodology.

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
    print("\n=== 1. CHECKING DEPENDENCIES ===")
    
    # Node.js
    print("- Node.js...")
    node_res = run_command(["node", "--version"], check=False)
    if node_res.returncode != 0:
        print("  [!] Node.js not found. Install via Volta: https://volta.sh/")
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
    print("\n=== 2. PYTHON VIRTUAL ENVIRONMENT ===")
    
    if not VENV_DIR.exists():
        print(f"- Creating venv in {VENV_DIR}...")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        print("  [OK] Virtual environment created")
    else:
        print(f"  [OK] venv already exists at {VENV_DIR}")
    
    # Activation instructions
    if os.name == "nt":
        print(f"  -> To activate: {VENV_DIR}\\Scripts\\activate")
    else:
        print(f"  -> To activate: source {VENV_DIR}/bin/activate")


def setup_skills():
    """Clone Antigravity Skills into .agent/skills."""
    print("\n=== 3. SKILLS SETUP ===")
    
    if not SKILLS_DIR.exists():
        print(f"- Cloning skills to {SKILLS_DIR}...")
        run_command(["git", "clone", SKILLS_REPO, str(SKILLS_DIR)])
        print("  [OK] Skills cloned")
    else:
        print(f"  [OK] Skills directory exists")
        print("- Pulling latest updates...")
        run_command(["git", "pull"], cwd=SKILLS_DIR, check=False)


def setup_git_flow():
    """Initialize Git repository and setup Git Flow branches."""
    print("\n=== 4. GIT FLOW SETUP (Sacchi Style) ===")
    
    # Check if Git is initialized
    git_dir = BASE_DIR / ".git"
    if not git_dir.exists():
        print("- Initializing Git repository...")
        run_command(["git", "init"])
        print("  [OK] Git initialized")
    else:
        print("  [OK] Git repository exists")
    
    # Check branches
    result = run_command(["git", "branch", "--list"], check=False)
    branches = result.stdout if result.stdout else ""
    
    # Ensure we have at least one commit
    log_result = run_command(["git", "log", "--oneline", "-n", "1"], check=False)
    if log_result.returncode != 0:
        print("- Creating initial commit...")
        # Stage .agent directory
        run_command(["git", "add", ".agent/"])
        run_command(["git", "commit", "-m", "Initial commit: Agentic environment setup"])
        print("  [OK] Initial commit created")
    
    # Create develop branch if it doesn't exist
    if "develop" not in branches:
        print("- Creating 'develop' branch...")
        run_command(["git", "checkout", "-b", "develop"])
        print("  [OK] 'develop' branch created and active")
    else:
        print("  [OK] 'develop' branch exists")
        # Switch to develop
        run_command(["git", "checkout", "develop"], check=False)
        print("  -> Switched to 'develop'")


def setup_gitignore():
    """Ensure .gitignore has safety entries."""
    print("\n=== 5. GITIGNORE SAFETY ===")
    
    gitignore_path = BASE_DIR / ".gitignore"
    required_entries = [
        ".env",
        ".env.*",
        "*.local",
        ".agent/.venv/",
        "node_modules/",
        "__pycache__/",
        "*.pyc",
    ]
    
    existing_entries = set()
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_entries = set(line.strip() for line in f if line.strip() and not line.startswith("#"))
    
    missing_entries = [e for e in required_entries if e not in existing_entries]
    
    if missing_entries:
        print(f"- Adding {len(missing_entries)} entries to .gitignore...")
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n# Agentic Environment Safety\n")
            for entry in missing_entries:
                f.write(f"{entry}\n")
                print(f"  + {entry}")
        print("  [OK] .gitignore updated")
    else:
        print("  [OK] .gitignore already configured")


def print_summary():
    """Print final summary and next steps."""
    print("\n" + "=" * 50)
    print("        [OK] AGENTIC ENVIRONMENT READY!")
    print("=" * 50)
    print("""
Structure:
  .agent/
  |-- bootstrap.py     (this script)
  |-- SACCHI.md        (methodology docs)
  |-- spec.md          (project specification)
  |-- .venv/           (Python environment)
  |-- skills/          (Antigravity skills)
  +-- workflows/       (slash command workflows)
      |-- tdd-cycle.md
      +-- feature-branch.md

Next Steps:
  1. Edit .agent/spec.md with your project goals
  2. Use /tdd-cycle for test-driven development
  3. Use /feature-branch for Git flow

Sacchi Principles:
  * Safety-first: Never work on main directly
  * Little-often: Atomic commits after each passing test
  * Double-check: Run all tests before merging
""")


def main():
    print("=" * 50)
    print("   AGENTIC ENVIRONMENT BOOTSTRAP")
    print("   Following Sacchi Methodology")
    print("=" * 50)
    
    check_dependencies()
    setup_venv()
    setup_skills()
    setup_git_flow()
    setup_gitignore()
    print_summary()


if __name__ == "__main__":
    main()
