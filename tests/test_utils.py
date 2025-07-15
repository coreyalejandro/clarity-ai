"""
Test utilities and helper functions for ClarityAI tests.
"""

import os
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import MagicMock

from clarity.scorer import Template


def create_temp_template(template_data: Dict[str, Any], temp_dir: Path) -> Path:
    """Create a temporary template file for testing."""
    template_path = temp_dir / "temp_template.yaml"
    with open(template_path, 'w') as f:
        yaml.dump(template_data, f)
    return template_path


def create_temp_text_file(content: str, temp_dir: Path, filename: str = "temp_text.txt") -> Path:
    """Create a temporary text file for testing."""
    text_path = temp_dir / filename
    with open(text_path, 'w') as f:
        f.write(content)
    return text_path


def assert_score_in_range(score: float, min_score: float = 0.0, max_score: float = 10.0):
    """Assert that a score is within the expected range."""
    assert isinstance(score, (int, float)), f"Score should be numeric, got {type(score)}"
    assert min_score <= score <= max_score, f"Score {score} not in range [{min_score}, {max_score}]"


def assert_template_valid(template: Template):
    """Assert that a template is valid and properly configured."""
    assert isinstance(template, Template), "Should be a Template instance"
    assert template.name, "Template should have a name"
    assert len(template.rules) > 0, "Template should have at least one rule"
    
    # Check that all rules have valid weights
    for rule in template.rules:
        assert rule.weight > 0, f"Rule {rule.rule_type} should have positive weight"


def mock_model_generate_response(tokenizer_mock: MagicMock, response_text: str):
    """Configure mock tokenizer to return specific response text."""
    # Mock the encode method to return token IDs
    tokenizer_mock.encode.return_value = [1, 2, 3, 4, 5]  # Mock token IDs
    
    # Mock the decode method to return the desired response
    tokenizer_mock.decode.return_value = response_text
    
    return tokenizer_mock


def create_mock_training_result(success: bool = True, run_id: str = "test_run") -> Dict[str, Any]:
    """Create a mock training result for testing."""
    if success:
        return {
            "status": "success",
            "run_id": run_id,
            "total_steps": 3,
            "average_reward": 0.75,
            "final_reward": 0.8,
            "output_dir": f"runs/{run_id}"
        }
    else:
        return {
            "status": "error",
            "error": "Mock training error",
            "run_id": run_id
        }


class MockCLIArgs:
    """Mock CLI arguments for testing command functions."""
    
    def __init__(self, **kwargs):
        # Set default values
        self.template = "test_template.yaml"
        self.text = None
        self.text_file = None
        self.detailed = False
        self.model = "microsoft/DialoGPT-small"
        self.name = "test_template"
        self.description = "Test template"
        self.output = "test_output.yaml"
        self.steps = 3
        self.learning_rate = 1e-5
        self.batch_size = 2
        
        # Override with provided values
        for key, value in kwargs.items():
            setattr(self, key, value)


def run_test_with_timeout(test_func, timeout_seconds: int = 30):
    """Run a test function with a timeout to prevent hanging tests."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Test timed out after {timeout_seconds} seconds")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = test_func()
        return result
    finally:
        # Cancel the timeout
        signal.alarm(0)


def assert_file_exists_and_valid(file_path: Path, expected_content: str = None):
    """Assert that a file exists and optionally check its content."""
    assert file_path.exists(), f"File should exist: {file_path}"
    assert file_path.is_file(), f"Path should be a file: {file_path}"
    
    if expected_content:
        with open(file_path, 'r') as f:
            content = f.read()
            assert expected_content in content, f"Expected content not found in {file_path}"


def get_test_data_path(filename: str) -> Path:
    """Get the path to a test data file."""
    return Path(__file__).parent / "fixtures" / filename