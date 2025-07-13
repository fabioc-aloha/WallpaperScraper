---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "create_file", "read_file"]
description: "Python package creation and distribution workflow"
---

# Package Development Episode Template

## Phase 1: Project Structure Setup
- Create proper package directory structure
- Configure pyproject.toml with build system and metadata
- Set up virtual environment and development dependencies
- Initialize version control and .gitignore

## Phase 2: Code Organization and Documentation
- Organize modules and packages logically
- Write comprehensive docstrings for all public APIs
- Create usage examples and API documentation
- Implement proper __init__.py files for packages

## Phase 3: Testing and Quality Assurance
- Develop comprehensive test suite with pytest
- Set up continuous integration for multiple Python versions
- Implement code quality checks (black, flake8, mypy)
- Achieve target code coverage and documentation standards

## Phase 4: Distribution and Maintenance
- Build and test package in clean environments
- Configure PyPI publishing with proper metadata
- Create release notes and version management
- Set up automated dependency updates and security scanning

Use Python packaging tools from ${workspaceFolder}/.venv
