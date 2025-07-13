---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "read_file", "get_errors"]
description: "Comprehensive Python testing workflow with pytest"
---

# Python Testing Episode Template

## Phase 1: Test Planning and Setup
- Analyze code structure and identify testable units
- Plan test cases covering happy path, edge cases, and error scenarios
- Set up pytest configuration in pyproject.toml
- Create necessary fixtures and test data in conftest.py

## Phase 2: Test Implementation
- Write unit tests following arrange-act-assert pattern
- Implement integration tests for complex workflows
- Use parametrize for testing multiple input scenarios
- Mock external dependencies and services appropriately

## Phase 3: Coverage and Quality Validation
- Run pytest with coverage reporting
- Analyze coverage reports to identify untested code
- Add missing tests to achieve target coverage
- Validate test reliability and fix flaky tests

## Phase 4: CI/CD Integration
- Configure pytest for continuous integration
- Set up automated test execution on code changes
- Implement test result reporting and notifications
- Monitor test performance and optimize slow tests

Use Python-specific patterns from ${workspaceFolder}/.venv
