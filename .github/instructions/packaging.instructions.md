---
applyTo: "**/setup.py,**/pyproject.toml,**/requirements*.txt,**/Pipfile"
description: "Python package management and distribution best practices"
---

# Python Packaging Procedural Memory

## Dependency Management
- Use requirements.txt for production dependencies
- Maintain requirements-dev.txt for development dependencies
- Pin exact versions for production: package==1.2.3
- Use version ranges for development: package>=1.2.0,<2.0.0
- Regularly update dependencies and test compatibility

## Virtual Environment Best Practices
- Always use .venv for virtual environments
- Include .venv/ in .gitignore
- Document Python version requirements clearly
- Use python -m venv instead of virtualenv for consistency
- Activate environment before installing dependencies

## Project Configuration
- Use pyproject.toml for modern Python project configuration
- Define build system requirements and backend
- Configure tool settings (black, pytest, mypy) in pyproject.toml
- Include project metadata: name, version, description, author
- Specify minimum Python version requirements

## Package Distribution
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Include comprehensive README.md with installation and usage
- Create CHANGELOG.md documenting version changes
- Use setup.py or pyproject.toml for package building
- Test package installation in clean environments

## Security and Maintenance
- Use pip-audit to check for security vulnerabilities
- Implement automated dependency updates with Dependabot
- Scan for outdated packages with pip-outdated
- Use safety package for security vulnerability checking
- Document security policies and vulnerability reporting
