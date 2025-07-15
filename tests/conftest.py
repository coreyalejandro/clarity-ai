"""
Shared test fixtures and configuration for ClarityAI tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock
import yaml

from clarity.scorer import Template, Rule
from clarity.trainer import TrainingConfig


@pytest.fixture
def temp_directory():
    """Provide a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_template():
    """Provide a standard test template."""
    template = Template("test_template")
    template.description = "A test template for unit testing"
    template.add_rule("contains_phrase", 2.0, phrase="helpful")
    template.add_rule("word_count", 1.0, min_words=10, max_words=100)
    template.add_rule("sentiment_positive", 1.0)
    return template


@pytest.fixture
def sample_template_yaml(temp_directory):
    """Provide a sample template YAML file."""
    template_data = {
        "name": "test_template",
        "description": "A test template",
        "rules": [
            {
                "type": "contains_phrase",
                "weight": 2.0,
                "phrase": "helpful"
            },
            {
                "type": "word_count",
                "weight": 1.0,
                "min_words": 10,
                "max_words": 100
            }
        ]
    }
    
    template_path = temp_directory / "test_template.yaml"
    with open(template_path, 'w') as f:
        yaml.dump(template_data, f)
    
    return template_path


@pytest.fixture
def sample_texts():
    """Provide sample texts for testing."""
    return [
        "This is a helpful explanation about machine learning concepts.",
        "Short text.",
        "This is a very long text that contains many words and should exceed the maximum word count limit set in the template rules for testing purposes.",
        "",
        "This text contains no positive sentiment and is quite negative in tone."
    ]


@pytest.fixture
def training_config():
    """Provide a test training configuration."""
    return TrainingConfig(
        model_name="microsoft/DialoGPT-small",
        template_path="test_template.yaml",
        max_steps=3,
        batch_size=2,
        learning_rate=1e-5,
        output_dir="test_runs"
    )


@pytest.fixture
def mock_model():
    """Provide a mock model for training tests."""
    mock = MagicMock()
    mock.generate.return_value = MagicMock()
    mock.save_pretrained = MagicMock()
    return mock


@pytest.fixture
def mock_tokenizer():
    """Provide a mock tokenizer for training tests."""
    mock = MagicMock()
    mock.encode.return_value = [1, 2, 3, 4, 5]
    mock.decode.return_value = "Generated response text"
    mock.pad_token = "<pad>"
    mock.eos_token = "<eos>"
    mock.pad_token_id = 0
    mock.eos_token_id = 1
    mock.save_pretrained = MagicMock()
    return mock


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up test files after each test."""
    yield
    # Clean up any test files that might have been created
    test_files = [
        "test_template.yaml",
        "test_output.txt",
        "test_runs",
        "htmlcov",
        "coverage.xml",
        ".coverage"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path, ignore_errors=True)
            else:
                os.remove(file_path)


# Test data constants
SAMPLE_TEMPLATE_DATA = {
    "name": "sample_template",
    "description": "Sample template for testing",
    "rules": [
        {"type": "contains_phrase", "weight": 2.0, "phrase": "helpful"},
        {"type": "word_count", "weight": 1.0, "min_words": 5, "max_words": 50},
        {"type": "sentiment_positive", "weight": 1.5}
    ]
}

SAMPLE_TEXTS = [
    "This is a helpful explanation.",
    "Short.",
    "This is a very long explanation that goes on and on with many words to test the word count limits.",
    "This is terrible and awful content.",
    ""
]