---
applyTo: "**/test_*.py,**/tests/**,**/conftest.py"
description: "Python testing patterns and pytest best practices"
---

# Python Testing Procedural Memory

## Pytest Framework Standards
- Use pytest fixtures for test setup and teardown
- Organize tests with clear arrange-act-assert pattern
- Use parametrize decorator for testing multiple scenarios
- Implement conftest.py for shared fixtures and configuration
- Use meaningful test function names that describe what is tested

## Test Organization and Structure
- Group related tests in classes using TestClass naming
- Use descriptive test method names: test_should_do_something_when_condition
- Create separate test files for each module being tested
- Organize tests to mirror source code structure
- Use pytest marks to categorize and filter tests

## Coverage and Quality Standards
- Maintain minimum 80% code coverage for critical modules
- Test both happy path and error scenarios
- Include edge cases and boundary condition testing
- Use mock objects to isolate units under test
- Write integration tests for API endpoints and database operations

## Fixtures and Test Data Management
- Create reusable fixtures for common test data
- Use factory_boy or similar for generating test objects
- Implement database fixtures with proper cleanup
- Use temporary files and directories for file system tests
- Mock external services and APIs in tests

## Performance and CI Integration
- Keep individual tests fast (under 100ms when possible)
- Use pytest-xdist for parallel test execution
- Implement smoke tests for critical functionality
- Configure pytest in pyproject.toml for consistency
- Generate coverage reports in multiple formats (HTML, XML)
