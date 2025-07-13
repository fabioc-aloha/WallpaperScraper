---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "read_file", "get_errors", "run_in_terminal"]
description: "Systematic Python code review and quality assessment workflows"
---

# Python Code Review Episode Template

## Phase 1: Initial Code Assessment
- Review code structure and organization
- Check adherence to Python PEP standards and style guidelines
- Analyze import structure and dependency management
- Assess overall code clarity and readability

## Phase 2: Functionality and Logic Review
- Verify correctness of algorithms and business logic
- Check error handling and edge case coverage
- Review security considerations and potential vulnerabilities
- Assess performance implications of implementation choices

## Phase 3: Quality and Maintainability Analysis
- Evaluate test coverage and test quality
- Check documentation completeness and accuracy
- Assess code reusability and modularity
- Review logging and debugging capabilities

## Phase 4: Recommendations and Action Items
- Provide specific, actionable feedback for improvements
- Prioritize issues by severity and impact
- Suggest refactoring opportunities and optimizations
- Document best practices and learning opportunities

Use Python code quality tools from ${workspaceFolder}/.venv
