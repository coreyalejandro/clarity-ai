"""
Unit tests for TrainingConfig class in ClarityAI.
"""

import pytest
from dataclasses import fields
from typing import Dict, Any

from clarity.trainer import TrainingConfig


class TestTrainingConfig:
    """Test the base TrainingConfig class functionality."""
    
    def test_training_config_creation_default(self):
        """Test TrainingConfig creation with default values."""
        config = TrainingConfig()
        
        # Test default model settings
        assert config.model_name == "microsoft/DialoGPT-small"
        assert config.template_path == "templates/demo.yaml"
        
        # Test default training hyperparameters
        assert config.learning_rate == 1.41e-5
        assert config.batch_size == 16
        assert config.mini_batch_size == 4
        assert config.ppo_epochs == 4
        assert config.max_steps == 20
        assert config.gradient_accumulation_steps == 1
        
        # Test default generation settings
        assert config.max_new_tokens == 50
        assert config.temperature == 0.7
        assert config.top_k == 50
        assert config.top_p == 0.95
        assert config.do_sample is True
        
        # Test default logging and output
        assert config.output_dir == "runs"
        assert config.log_with == "tensorboard"
        assert config.save_every == 5
        
        # Test default advanced settings
        assert config.cliprange == 0.2
        assert config.cliprange_value == 0.2
        assert config.vf_coef == 0.1
        assert config.gamma == 1.0
        assert config.lam == 0.95
    
    def test_training_config_creation_with_custom_values(self):
        """Test TrainingConfig creation with custom values."""
        config = TrainingConfig(
            model_name="gpt2",
            template_path="custom/template.yaml",
            learning_rate=2e-5,
            batch_size=32,
            max_steps=100,
            temperature=0.8,
            output_dir="custom_runs"
        )
        
        # Test custom values
        assert config.model_name == "gpt2"
        assert config.template_path == "custom/template.yaml"
        assert config.learning_rate == 2e-5
        assert config.batch_size == 32
        assert config.max_steps == 100
        assert config.temperature == 0.8
        assert config.output_dir == "custom_runs"
        
        # Test that other values remain default
        assert config.mini_batch_size == 4  # Default
        assert config.top_k == 50  # Default
    
    def test_training_config_all_parameters(self):
        """Test TrainingConfig with all parameters specified."""
        config = TrainingConfig(
            # Model settings
            model_name="custom/model",
            template_path="custom/template.yaml",
            
            # Training hyperparameters
            learning_rate=3e-5,
            batch_size=8,
            mini_batch_size=2,
            ppo_epochs=6,
            max_steps=50,
            gradient_accumulation_steps=2,
            
            # Generation settings
            max_new_tokens=100,
            temperature=0.9,
            top_k=40,
            top_p=0.85,
            do_sample=False,
            
            # Logging and output
            output_dir="test_runs",
            log_with="wandb",
            save_every=10,
            
            # Advanced settings
            cliprange=0.3,
            cliprange_value=0.3,
            vf_coef=0.2,
            gamma=0.99,
            lam=0.9
        )
        
        # Verify all values
        assert config.model_name == "custom/model"
        assert config.template_path == "custom/template.yaml"
        assert config.learning_rate == 3e-5
        assert config.batch_size == 8
        assert config.mini_batch_size == 2
        assert config.ppo_epochs == 6
        assert config.max_steps == 50
        assert config.gradient_accumulation_steps == 2
        assert config.max_new_tokens == 100
        assert config.temperature == 0.9
        assert config.top_k == 40
        assert config.top_p == 0.85
        assert config.do_sample is False
        assert config.output_dir == "test_runs"
        assert config.log_with == "wandb"
        assert config.save_every == 10
        assert config.cliprange == 0.3
        assert config.cliprange_value == 0.3
        assert config.vf_coef == 0.2
        assert config.gamma == 0.99
        assert config.lam == 0.9


class TestTrainingConfigSerialization:
    """Test TrainingConfig serialization and deserialization."""
    
    def test_to_dict_default_config(self):
        """Test converting default config to dictionary."""
        config = TrainingConfig()
        config_dict = config.to_dict()
        
        # Check that it's a dictionary
        assert isinstance(config_dict, dict)
        
        # Check that all fields are present
        expected_fields = {field.name for field in fields(TrainingConfig)}
        assert set(config_dict.keys()) == expected_fields
        
        # Check some key values
        assert config_dict["model_name"] == "microsoft/DialoGPT-small"
        assert config_dict["learning_rate"] == 1.41e-5
        assert config_dict["batch_size"] == 16
        assert config_dict["max_steps"] == 20
    
    def test_to_dict_custom_config(self):
        """Test converting custom config to dictionary."""
        config = TrainingConfig(
            model_name="gpt2",
            learning_rate=2e-5,
            batch_size=32,
            temperature=0.8
        )
        config_dict = config.to_dict()
        
        # Check custom values
        assert config_dict["model_name"] == "gpt2"
        assert config_dict["learning_rate"] == 2e-5
        assert config_dict["batch_size"] == 32
        assert config_dict["temperature"] == 0.8
        
        # Check default values are preserved
        assert config_dict["mini_batch_size"] == 4
        assert config_dict["max_steps"] == 20
    
    def test_from_dict_default_values(self):
        """Test creating config from dictionary with default values."""
        config_dict = {
            "model_name": "microsoft/DialoGPT-small",
            "template_path": "templates/demo.yaml",
            "learning_rate": 1.41e-5,
            "batch_size": 16,
            "mini_batch_size": 4,
            "ppo_epochs": 4,
            "max_steps": 20,
            "gradient_accumulation_steps": 1,
            "max_new_tokens": 50,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": True,
            "output_dir": "runs",
            "log_with": "tensorboard",
            "save_every": 5,
            "cliprange": 0.2,
            "cliprange_value": 0.2,
            "vf_coef": 0.1,
            "gamma": 1.0,
            "lam": 0.95
        }
        
        config = TrainingConfig.from_dict(config_dict)
        
        # Verify all values
        assert config.model_name == "microsoft/DialoGPT-small"
        assert config.learning_rate == 1.41e-5
        assert config.batch_size == 16
        assert config.max_steps == 20
        assert config.temperature == 0.7
        assert config.do_sample is True
    
    def test_from_dict_custom_values(self):
        """Test creating config from dictionary with custom values."""
        config_dict = {
            "model_name": "custom/model",
            "template_path": "custom/template.yaml",
            "learning_rate": 3e-5,
            "batch_size": 8,
            "mini_batch_size": 2,
            "ppo_epochs": 6,
            "max_steps": 100,
            "gradient_accumulation_steps": 4,
            "max_new_tokens": 75,
            "temperature": 0.9,
            "top_k": 30,
            "top_p": 0.8,
            "do_sample": False,
            "output_dir": "custom_output",
            "log_with": "wandb",
            "save_every": 15,
            "cliprange": 0.25,
            "cliprange_value": 0.25,
            "vf_coef": 0.15,
            "gamma": 0.95,
            "lam": 0.9
        }
        
        config = TrainingConfig.from_dict(config_dict)
        
        # Verify custom values
        assert config.model_name == "custom/model"
        assert config.template_path == "custom/template.yaml"
        assert config.learning_rate == 3e-5
        assert config.batch_size == 8
        assert config.mini_batch_size == 2
        assert config.max_steps == 100
        assert config.temperature == 0.9
        assert config.do_sample is False
        assert config.output_dir == "custom_output"
    
    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves all values."""
        original_config = TrainingConfig(
            model_name="test/model",
            learning_rate=5e-5,
            batch_size=64,
            max_steps=200,
            temperature=0.6,
            top_k=25,
            do_sample=True,
            output_dir="test_output"
        )
        
        # Convert to dict and back
        config_dict = original_config.to_dict()
        restored_config = TrainingConfig.from_dict(config_dict)
        
        # Compare all fields
        for field in fields(TrainingConfig):
            original_value = getattr(original_config, field.name)
            restored_value = getattr(restored_config, field.name)
            assert original_value == restored_value, f"Field {field.name} mismatch: {original_value} != {restored_value}"
    
    def test_from_dict_partial_data(self):
        """Test creating config from dictionary with only some fields."""
        partial_dict = {
            "model_name": "partial/model",
            "learning_rate": 4e-5,
            "batch_size": 24
        }
        
        # Should work with partial data, using defaults for missing fields
        config = TrainingConfig.from_dict(partial_dict)
        
        # Check specified values
        assert config.model_name == "partial/model"
        assert config.learning_rate == 4e-5
        assert config.batch_size == 24
        
        # Check that defaults are used for unspecified fields
        assert config.template_path == "templates/demo.yaml"  # Default
        assert config.max_steps == 20  # Default
        assert config.temperature == 0.7  # Default
    
    def test_from_dict_extra_fields(self):
        """Test creating config from dictionary with extra fields."""
        config_dict = {
            "model_name": "test/model",
            "template_path": "test/template.yaml",
            "learning_rate": 2e-5,
            "batch_size": 16,
            "mini_batch_size": 4,
            "ppo_epochs": 4,
            "max_steps": 20,
            "gradient_accumulation_steps": 1,
            "max_new_tokens": 50,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 0.95,
            "do_sample": True,
            "output_dir": "runs",
            "log_with": "tensorboard",
            "save_every": 5,
            "cliprange": 0.2,
            "cliprange_value": 0.2,
            "vf_coef": 0.1,
            "gamma": 1.0,
            "lam": 0.95,
            "extra_field": "should_be_ignored"  # Extra field
        }
        
        # Should raise TypeError due to unexpected keyword argument
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            TrainingConfig.from_dict(config_dict)


class TestTrainingConfigValidation:
    """Test TrainingConfig parameter validation and edge cases."""
    
    def test_numeric_parameter_types(self):
        """Test that numeric parameters accept correct types."""
        config = TrainingConfig(
            learning_rate=1e-5,  # float
            batch_size=16,       # int
            temperature=0.7,     # float
            max_steps=100,       # int
            top_k=50,           # int
            top_p=0.95,         # float
            gamma=1.0,          # float
            lam=0.95            # float
        )
        
        assert isinstance(config.learning_rate, float)
        assert isinstance(config.batch_size, int)
        assert isinstance(config.temperature, float)
        assert isinstance(config.max_steps, int)
        assert isinstance(config.top_k, int)
        assert isinstance(config.top_p, float)
        assert isinstance(config.gamma, float)
        assert isinstance(config.lam, float)
    
    def test_boolean_parameter_types(self):
        """Test that boolean parameters work correctly."""
        config_true = TrainingConfig(do_sample=True)
        config_false = TrainingConfig(do_sample=False)
        
        assert config_true.do_sample is True
        assert config_false.do_sample is False
        assert isinstance(config_true.do_sample, bool)
        assert isinstance(config_false.do_sample, bool)
    
    def test_string_parameter_types(self):
        """Test that string parameters work correctly."""
        config = TrainingConfig(
            model_name="custom/model",
            template_path="/path/to/template.yaml",
            output_dir="/custom/output",
            log_with="wandb"
        )
        
        assert isinstance(config.model_name, str)
        assert isinstance(config.template_path, str)
        assert isinstance(config.output_dir, str)
        assert isinstance(config.log_with, str)
    
    def test_edge_case_numeric_values(self):
        """Test edge case numeric values."""
        config = TrainingConfig(
            learning_rate=0.0,      # Zero learning rate
            batch_size=1,           # Minimum batch size
            max_steps=1,            # Minimum steps
            temperature=0.0,        # Zero temperature
            top_k=1,               # Minimum top_k
            top_p=0.0,             # Minimum top_p
            gamma=0.0,             # Zero gamma
            lam=0.0                # Zero lambda
        )
        
        assert config.learning_rate == 0.0
        assert config.batch_size == 1
        assert config.max_steps == 1
        assert config.temperature == 0.0
        assert config.top_k == 1
        assert config.top_p == 0.0
        assert config.gamma == 0.0
        assert config.lam == 0.0
    
    def test_large_numeric_values(self):
        """Test large numeric values."""
        config = TrainingConfig(
            learning_rate=1.0,      # Large learning rate
            batch_size=1000,        # Large batch size
            max_steps=10000,        # Many steps
            temperature=2.0,        # High temperature
            top_k=1000,            # Large top_k
            top_p=1.0,             # Maximum top_p
            max_new_tokens=1000,   # Many tokens
            save_every=1000        # Large save interval
        )
        
        assert config.learning_rate == 1.0
        assert config.batch_size == 1000
        assert config.max_steps == 10000
        assert config.temperature == 2.0
        assert config.top_k == 1000
        assert config.top_p == 1.0
        assert config.max_new_tokens == 1000
        assert config.save_every == 1000


class TestTrainingConfigEquality:
    """Test TrainingConfig equality and comparison."""
    
    def test_config_equality_same_values(self):
        """Test that configs with same values are equal."""
        config1 = TrainingConfig(
            model_name="test/model",
            learning_rate=2e-5,
            batch_size=32
        )
        config2 = TrainingConfig(
            model_name="test/model",
            learning_rate=2e-5,
            batch_size=32
        )
        
        # Dataclasses should be equal if all fields match
        assert config1 == config2
    
    def test_config_equality_different_values(self):
        """Test that configs with different values are not equal."""
        config1 = TrainingConfig(model_name="model1")
        config2 = TrainingConfig(model_name="model2")
        
        assert config1 != config2
    
    def test_config_equality_one_field_different(self):
        """Test that configs differing in one field are not equal."""
        config1 = TrainingConfig(
            model_name="same/model",
            learning_rate=2e-5,
            batch_size=32
        )
        config2 = TrainingConfig(
            model_name="same/model",
            learning_rate=2e-5,
            batch_size=16  # Different batch size
        )
        
        assert config1 != config2


class TestTrainingConfigIntegration:
    """Test TrainingConfig integration scenarios."""
    
    def test_config_with_realistic_training_values(self):
        """Test config with realistic training parameter combinations."""
        # Small model, quick training
        quick_config = TrainingConfig(
            model_name="microsoft/DialoGPT-small",
            learning_rate=1e-4,
            batch_size=8,
            max_steps=10,
            temperature=0.7,
            max_new_tokens=30
        )
        
        assert quick_config.model_name == "microsoft/DialoGPT-small"
        assert quick_config.learning_rate == 1e-4
        assert quick_config.max_steps == 10
        
        # Larger model, longer training
        extended_config = TrainingConfig(
            model_name="microsoft/DialoGPT-medium",
            learning_rate=5e-6,
            batch_size=4,
            max_steps=100,
            temperature=0.8,
            max_new_tokens=100,
            save_every=20
        )
        
        assert extended_config.model_name == "microsoft/DialoGPT-medium"
        assert extended_config.learning_rate == 5e-6
        assert extended_config.max_steps == 100
        assert extended_config.save_every == 20
    
    def test_config_serialization_for_persistence(self):
        """Test config serialization for saving/loading scenarios."""
        original_config = TrainingConfig(
            model_name="production/model",
            template_path="production/template.yaml",
            learning_rate=1.5e-5,
            batch_size=16,
            max_steps=500,
            output_dir="production_runs",
            save_every=50
        )
        
        # Simulate saving to file (convert to dict)
        saved_data = original_config.to_dict()
        
        # Simulate loading from file (create from dict)
        loaded_config = TrainingConfig.from_dict(saved_data)
        
        # Should be identical
        assert loaded_config == original_config
        assert loaded_config.model_name == "production/model"
        assert loaded_config.template_path == "production/template.yaml"
        assert loaded_config.learning_rate == 1.5e-5
        assert loaded_config.output_dir == "production_runs"
    
    def test_config_parameter_override_scenarios(self):
        """Test common parameter override scenarios."""
        # Base config
        base_config = TrainingConfig()
        
        # Override for debugging (small values)
        debug_config = TrainingConfig(
            model_name=base_config.model_name,  # Keep same model
            template_path=base_config.template_path,  # Keep same template
            learning_rate=1e-3,  # Higher learning rate for quick testing
            batch_size=2,        # Small batch for memory efficiency
            max_steps=5,         # Few steps for quick testing
            save_every=1         # Save every step for debugging
        )
        
        assert debug_config.model_name == base_config.model_name
        assert debug_config.template_path == base_config.template_path
        assert debug_config.learning_rate == 1e-3
        assert debug_config.batch_size == 2
        assert debug_config.max_steps == 5
        assert debug_config.save_every == 1
        
        # Override for production (optimized values)
        production_config = TrainingConfig(
            model_name="production/optimized-model",
            template_path="production/optimized-template.yaml",
            learning_rate=5e-6,   # Lower learning rate for stability
            batch_size=32,        # Larger batch for efficiency
            max_steps=1000,       # Many steps for thorough training
            save_every=100,       # Less frequent saves for efficiency
            output_dir="production_runs"
        )
        
        assert production_config.model_name == "production/optimized-model"
        assert production_config.learning_rate == 5e-6
        assert production_config.batch_size == 32
        assert production_config.max_steps == 1000
        assert production_config.save_every == 100
    
    def test_config_field_completeness(self):
        """Test that all expected fields are present in TrainingConfig."""
        config = TrainingConfig()
        
        # Get all field names from the dataclass
        field_names = {field.name for field in fields(TrainingConfig)}
        
        # Expected categories of fields
        expected_model_fields = {"model_name", "template_path"}
        expected_training_fields = {
            "learning_rate", "batch_size", "mini_batch_size", "ppo_epochs", 
            "max_steps", "gradient_accumulation_steps"
        }
        expected_generation_fields = {
            "max_new_tokens", "temperature", "top_k", "top_p", "do_sample"
        }
        expected_output_fields = {"output_dir", "log_with", "save_every"}
        expected_advanced_fields = {
            "cliprange", "cliprange_value", "vf_coef", "gamma", "lam"
        }
        
        # Check that all expected fields are present
        assert expected_model_fields.issubset(field_names)
        assert expected_training_fields.issubset(field_names)
        assert expected_generation_fields.issubset(field_names)
        assert expected_output_fields.issubset(field_names)
        assert expected_advanced_fields.issubset(field_names)
        
        # Check total field count matches expectation
        total_expected = (
            len(expected_model_fields) + 
            len(expected_training_fields) + 
            len(expected_generation_fields) + 
            len(expected_output_fields) + 
            len(expected_advanced_fields)
        )
        assert len(field_names) == total_expected