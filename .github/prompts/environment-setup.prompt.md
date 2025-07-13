---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "read_file", "create_file"]
description: "Python virtual environment and dependency management workflow"
---

# Environment Setup Episode Template

## Phase 1: Virtual Environment Creation
- Create .venv virtual environment in project root
- Activate environment and upgrade pip to latest version
- Configure VS Code Python interpreter to use .venv
- Set up environment variables in .env file

## Phase 2: Dependency Management
- Create requirements.txt for production dependencies
- Set up requirements-dev.txt for development tools
- Install and configure development tools (pytest, black, flake8)
- Pin dependency versions for reproducible environments

## Phase 3: Configuration and Tools
- Configure pyproject.toml for tool settings
- Set up pre-commit hooks for code quality
- Configure IDE settings for Python development
- Create .gitignore with Python-specific patterns

## Phase 4: Validation and Documentation
- Test environment setup in clean state
- Document installation and setup procedures
- Validate all development tools work correctly
- Create troubleshooting guide for common issues

Use Python environment management from ${workspaceFolder}/.venv
