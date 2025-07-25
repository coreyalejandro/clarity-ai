# ClarityAI Testing Guide

This document provides information about the ClarityAI test suite, how to run tests, and guidelines for contributing new tests.

## Test Organization

The test suite is organized into the following directories:

- **tests/unit/**: Unit tests for individual components
- **tests/integration/**: End-to-end and workflow tests
- **tests/performance/**: Performance benchmarks and resource monitoring
- **tests/fixtures/**: Test data and resources

## Running Tests

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install -e .
pip install pytest pytest-cov
```

For performance tests, additional dependencies are required:

```bash
pip install psutil
```

### Running the Full Test Suite

To run all tests:

```bash
pytest
```

### Running Specific Test Categories

To run only unit tests:

```bash
pytest tests/unit
# or
pytest -m unit
```

To run only integration tests:

```bash
pytest tests/integration
# or
pytest -m integration
```

To run only performance tests:

```bash
pytest tests/performance
# or
pytest -m performance
```

### Running with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=clarity --cov-report=term-missing
```

For HTML coverage report:

```bash
pytest --cov=clarity --cov-report=html
# Report will be in htmlcov/index.html
```

## Test Markers

The following markers are available for categorizing tests:

- `unit`: Unit tests
- `integration`: Integration tests
- `performance`: Performance tests
- `slow`: Slow running tests (excluded from CI by default)

Example usage:

```python
@pytest.mark.unit
def test_something():
    # Test code here
```

## Writing New Tests

### Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test functions should be named `test_*`

### Test Structure

Each test should follow this general structure:

1. **Arrange**: Set up the test data and environment
2. **Act**: Execute the code being tested
3. **Assert**: Verify the results

Example:

```python
def test_template_evaluation():
    # Arrange
    template = Template("test")
    template.add_rule("contains_phrase", 1.0, phrase="test")
    
    # Act
    result = template.evaluate("This is a test")
    
    # Assert
    assert result == 1.0
```

### Using Fixtures

Common test setup can be extracted into fixtures:

```python
@pytest.fixture
def sample_template():
    template = Template("test")
    template.add_rule("contains_phrase", 1.0, phrase="test")
    return template

def test_with_fixture(sample_template):
    result = sample_template.evaluate("This is a test")
    assert result == 1.0
```

### Performance Tests

Performance tests should:

1. Measure execution time and/or resource usage
2. Log relevant metrics
3. Assert against reasonable thresholds
4. Be marked with `@pytest.mark.performance`

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   - Ensure all required packages are installed
   - Check for version conflicts

2. **Test discovery issues**:
   - Verify test file names follow the convention `test_*.py`
   - Ensure test functions are named `test_*`

3. **Slow tests**:
   - Mark slow tests with `@pytest.mark.slow`
   - Skip slow tests in CI with `pytest -m "not slow"`

4. **Resource-intensive tests**:
   - Use appropriate skipping for tests that require specific resources
   - Example: `@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")`

### Getting Help

If you encounter issues with the test suite:

1. Check the pytest documentation: https://docs.pytest.org/
2. Review existing tests for examples
3. File an issue in the GitHub repository