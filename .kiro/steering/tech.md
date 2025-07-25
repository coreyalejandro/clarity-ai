---
inclusion: always
---

# ClarityAI Technical Stack

## Core Technologies

- **Language**: Python 3.9+
- **ML Framework**: PyTorch, Transformers (Hugging Face)
- **Training**: TRL (Transformer Reinforcement Learning)
- **UI**: Streamlit
- **Data Format**: YAML for templates and configuration

## Key Dependencies

- `torch`: Neural network and tensor operations
- `transformers`: Pre-trained models and tokenizers
- `trl`: Reinforcement learning for transformer models
- `streamlit`: Web interface for rubric building
- `pyyaml`: YAML parsing and generation
- `numpy`: Numerical operations

## Project Structure

ClarityAI is structured as a Python package with a command-line interface and optional web UI.

## Common Commands

### Installation

```bash
# Install in development mode
pip install -e .
```

### CLI Usage

```bash
# Score text with a template
clarity score example.txt --template rubric.yaml

# Score text directly
clarity score --text "Text to evaluate" --template rubric.yaml --detailed

# Run a demo with a model
clarity demo --model microsoft/DialoGPT-small

# Create a new template
clarity create-template --name "my-template" --output templates/my-template.yaml

# Train a model
clarity train --model microsoft/DialoGPT-small --template templates/my-template.yaml --steps 20
```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
pytest -m unit
pytest -m integration
pytest -m performance

# Run with coverage
pytest --cov=clarity
```

### Web UI

```bash
# Start the Streamlit UI
streamlit run app.py
```