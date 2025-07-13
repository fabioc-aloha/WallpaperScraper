---
applyTo: "**/*.py,**/setup.py,**/conftest.py"
description: "Python standards and development best practices"
---

# Python Standards Procedural Memory

## PEP Compliance and Code Style
- Follow PEP 8 style guidelines for code formatting
- Use PEP 257 conventions for docstrings
- Apply PEP 484 type hints for function parameters and return values
- Follow PEP 20 (Zen of Python) principles for code design
- Use Black formatter with 88-character line length

## Pythonic Programming Patterns
- Use list comprehensions and generator expressions appropriately
- Prefer context managers (with statements) for resource management
- Use enumerate() instead of manual indexing in loops
- Apply duck typing and EAFP (Easier to Ask for Forgiveness than Permission)
- Utilize built-in functions and standard library modules

## Code Organization and Structure
- Organize imports: standard library, third-party, local imports
- Use __init__.py files to create packages
- Follow single responsibility principle for functions and classes
- Use meaningful names that describe purpose and behavior
- Keep functions focused and limit to 20-30 lines when possible

## Error Handling and Debugging
- Use specific exception types rather than broad except clauses
- Implement proper logging with the logging module
- Use assert statements for debugging and testing assumptions
- Handle edge cases and validate input parameters
- Provide meaningful error messages and context

## Performance and Memory Optimization
- Use generators for large datasets to save memory
- Leverage itertools for efficient iteration patterns
- Profile code with cProfile or line_profiler
- Use slots for classes with fixed attributes
- Consider numpy arrays for numerical computations
