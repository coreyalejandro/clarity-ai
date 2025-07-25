---
inclusion: always
---

# ClarityAI Project Structure

## Directory Organization

- **clarity/**: Core package directory
  - **__init__.py**: Package initialization
  - **cli.py**: Command-line interface implementation
  - **scorer.py**: Scoring engine and template system
  - **trainer.py**: Model training functionality

- **tests/**: Test suite
  - **unit/**: Unit tests for individual components
  - **integration/**: End-to-end and workflow tests
  - **performance/**: Performance benchmarks
  - **fixtures/**: Test data and resources

- **templates/**: Example and default templates
  - **demo.yaml**: Default template for demos

- **runs/**: Training run outputs and checkpoints
  - **training_ledger.yaml**: Record of all training runs

- **app.py**: Streamlit web application

## Code Organization

### Core Components

1. **Rule System**: Defined in `clarity/scorer.py`
   - Individual scoring rules with types, weights, and parameters
   - Rule evaluation logic for different criteria types

2. **Template System**: Defined in `clarity/scorer.py`
   - Template class for managing collections of rules
   - YAML serialization and deserialization
   - Scoring functions for text evaluation

3. **Training System**: Defined in `clarity/trainer.py`
   - Training configuration and run tracking
   - Model loading and optimization
   - Reward computation using templates

4. **CLI**: Defined in `clarity/cli.py`
   - Command parsing and routing
   - User interface for scoring, training, and demos

5. **Web UI**: Defined in `app.py`
   - Interactive template editor
   - Live scoring and visualization
   - Batch processing capabilities

## Conventions

- **Python Style**: PEP 8 compliant with type hints
- **Documentation**: Docstrings for classes and functions
- **Testing**: Pytest with markers for test categories
- **Coverage**: Minimum 80% test coverage required
- **Configuration**: YAML for templates and settings