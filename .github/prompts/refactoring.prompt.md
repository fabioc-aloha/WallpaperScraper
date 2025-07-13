---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "read_file", "get_errors", "run_in_terminal"]
description: "Python code refactoring and optimization methodologies"
---

# Python Refactoring Episode Template

## Phase 1: Code Analysis and Assessment
- Identify code smells and areas needing improvement
- Analyze code complexity and maintainability metrics
- Review adherence to Python best practices and PEP standards
- Assess performance bottlenecks and optimization opportunities

## Phase 2: Refactoring Strategy Planning
- Prioritize refactoring tasks based on impact and effort
- Plan incremental changes to maintain working code
- Identify opportunities for extracting reusable components
- Design improved architecture and code organization

## Phase 3: Implementation with Safety Measures
- Ensure comprehensive test coverage before refactoring
- Make small, focused changes with immediate testing
- Apply design patterns and Pythonic idioms appropriately
- Maintain backward compatibility where necessary

## Phase 4: Validation and Documentation
- Run full test suite to verify functionality preservation
- Measure performance improvements and code quality metrics
- Update documentation to reflect architectural changes
- Review with team and gather feedback on improvements

Use Python refactoring tools from ${workspaceFolder}/.venv
