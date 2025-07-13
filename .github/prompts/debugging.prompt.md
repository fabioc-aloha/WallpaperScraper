---
mode: "agent"
model: "gpt-4"
tools: ["workspace", "run_in_terminal", "read_file", "get_errors"]
description: "Python debugging and troubleshooting procedures with pdb"
---

# Python Debugging Episode Template

## Phase 1: Problem Analysis and Reproduction
- Analyze error messages and stack traces systematically
- Identify the root cause and affected code sections
- Create minimal reproducible examples
- Document steps to reproduce the issue consistently

## Phase 2: Debugging Strategy Selection
- Choose appropriate debugging tools (pdb, logging, print statements)
- Set strategic breakpoints in suspected problem areas
- Plan systematic investigation approach
- Prepare test cases to validate fixes

## Phase 3: Investigation and Root Cause Analysis
- Use pdb for interactive debugging sessions
- Examine variable states and execution flow
- Test hypotheses about the root cause
- Document findings and insights during investigation

## Phase 4: Solution Implementation and Validation
- Implement targeted fixes based on root cause analysis
- Write tests to prevent regression
- Validate fix with original reproduction steps
- Update documentation and error handling as needed

Use Python debugging tools from ${workspaceFolder}/.venv
