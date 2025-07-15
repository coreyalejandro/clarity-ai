"""
Unit tests for training utility functions in ClarityAI.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import Mock, MagicMock, patch, mock_open
from typing import Dict, Any

from clarity.trainer import train_model, load_training_ledger, TrainingConfig, TrainingRun, ClarityTrainer


class TestTrainModelFunction:
    """Test the train_model() convenience function."""
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_basic_parameters(self, mock_trainer_class):
        """Test train_model with basic parameters."""
        # Setup mock
        mock_trainer_instance = Mock()
        mock_trainer_instance.train.return_value = {
            "status": "success",
            "run_id": "test_run",
            "total_steps": 20,
            "average_reward": 0.75,
            "final_reward": 0.8
        }
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function
        result = train_model(
            model_name="test/model",
            template_path="test/template.yaml"
        )
        
        # Verify trainer was created with correct config
        mock_trainer_class.assert_called_once()
        config_arg = mock_trainer_class.call_args[0][0]
        assert isinstance(config_arg, TrainingConfig)
        assert config_arg.model_name == "test/model"
        assert config_arg.template_path == "test/template.yaml"
        assert config_arg.max_steps == 20  # Default
        assert config_arg.learning_rate == 1.41e-5  # Default
        assert config_arg.batch_size == 16  # Default
        assert config_arg.output_dir == "runs"  # Default
        
        # Verify train was called
        mock_trainer_instance.train.assert_called_once()
        
        # Verify result
        assert result["status"] == "success"
        assert result["run_id"] == "test_run"
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_custom_parameters(self, mock_trainer_class):
        """Test train_model with custom parameters."""
        # Setup mock
        mock_trainer_instance = Mock()
        mock_trainer_instance.train.return_value = {"status": "success"}
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function with custom parameters
        result = train_model(
            model_name="custom/model",
            template_path="custom/template.yaml",
            max_steps=50,
            learning_rate=2e-5,
            batch_size=32,
            output_dir="custom_runs"
        )
        
        # Verify trainer was created with custom config
        config_arg = mock_trainer_class.call_args[0][0]
        assert config_arg.model_name == "custom/model"
        assert config_arg.template_path == "custom/template.yaml"
        assert config_arg.max_steps == 50
        assert config_arg.learning_rate == 2e-5
        assert config_arg.batch_size == 32
        assert config_arg.output_dir == "custom_runs"
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_with_kwargs(self, mock_trainer_class):
        """Test train_model with additional keyword arguments."""
        # Setup mock
        mock_trainer_instance = Mock()
        mock_trainer_instance.train.return_value = {"status": "success"}
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function with additional kwargs
        result = train_model(
            model_name="test/model",
            template_path="test/template.yaml",
            temperature=0.9,
            top_k=30,
            save_every=10,
            mini_batch_size=8
        )
        
        # Verify trainer was created with kwargs passed through
        config_arg = mock_trainer_class.call_args[0][0]
        assert config_arg.temperature == 0.9
        assert config_arg.top_k == 30
        assert config_arg.save_every == 10
        assert config_arg.mini_batch_size == 8
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_training_success(self, mock_trainer_class):
        """Test train_model with successful training result."""
        # Setup mock with detailed success result
        mock_trainer_instance = Mock()
        expected_result = {
            "status": "success",
            "run_id": "run_20240101_120000",
            "total_steps": 25,
            "average_reward": 0.72,
            "final_reward": 0.85,
            "output_dir": "runs/run_20240101_120000"
        }
        mock_trainer_instance.train.return_value = expected_result
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function
        result = train_model("test/model", "test/template.yaml", max_steps=25)
        
        # Verify result is passed through correctly
        assert result == expected_result
        assert result["status"] == "success"
        assert result["total_steps"] == 25
        assert result["average_reward"] == 0.72
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_training_failure(self, mock_trainer_class):
        """Test train_model with training failure."""
        # Setup mock with failure result
        mock_trainer_instance = Mock()
        expected_result = {
            "status": "error",
            "error": "Template not found: test/template.yaml",
            "run_id": "run_20240101_120000"
        }
        mock_trainer_instance.train.return_value = expected_result
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function
        result = train_model("test/model", "nonexistent/template.yaml")
        
        # Verify error result is passed through
        assert result == expected_result
        assert result["status"] == "error"
        assert "Template not found" in result["error"]
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_trainer_creation_error(self, mock_trainer_class):
        """Test train_model when trainer creation fails."""
        # Setup mock to raise error during creation
        mock_trainer_class.side_effect = Exception("Trainer creation failed")
        
        # Call function and expect exception to propagate
        with pytest.raises(Exception, match="Trainer creation failed"):
            train_model("test/model", "test/template.yaml")
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_train_method_error(self, mock_trainer_class):
        """Test train_model when train method fails."""
        # Setup mock where train method raises error
        mock_trainer_instance = Mock()
        mock_trainer_instance.train.side_effect = Exception("Training failed")
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call function and expect exception to propagate
        with pytest.raises(Exception, match="Training failed"):
            train_model("test/model", "test/template.yaml")
    
    def test_train_model_parameter_validation(self):
        """Test train_model parameter types and validation."""
        # Test that function accepts correct parameter types
        with patch('clarity.trainer.ClarityTrainer') as mock_trainer_class:
            mock_trainer_instance = Mock()
            mock_trainer_instance.train.return_value = {"status": "success"}
            mock_trainer_class.return_value = mock_trainer_instance
            
            # Test with various parameter types
            result = train_model(
                model_name="test/model",
                template_path="test/template.yaml",
                max_steps=100,          # int
                learning_rate=1e-4,     # float
                batch_size=8,           # int
                output_dir="test_dir",  # str
                temperature=0.8,        # float (kwarg)
                do_sample=True          # bool (kwarg)
            )
            
            # Verify config was created with correct types
            config_arg = mock_trainer_class.call_args[0][0]
            assert isinstance(config_arg.max_steps, int)
            assert isinstance(config_arg.learning_rate, float)
            assert isinstance(config_arg.batch_size, int)
            assert isinstance(config_arg.output_dir, str)
            assert isinstance(config_arg.temperature, float)
            assert isinstance(config_arg.do_sample, bool)


class TestLoadTrainingLedgerFunction:
    """Test the load_training_ledger() function."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_success(self, mock_yaml_load, mock_exists, mock_file):
        """Test successful loading of training ledger."""
        # Setup mocks
        mock_exists.return_value = True
        mock_ledger_data = {
            'runs': [
                {
                    'run_id': 'run_1',
                    'model_name': 'test/model1',
                    'template_path': 'test/template1.yaml',
                    'config': {
                        'model_name': 'test/model1',
                        'template_path': 'test/template1.yaml',
                        'learning_rate': 1e-5,
                        'batch_size': 16,
                        'mini_batch_size': 4,
                        'ppo_epochs': 4,
                        'max_steps': 20,
                        'gradient_accumulation_steps': 1,
                        'max_new_tokens': 50,
                        'temperature': 0.7,
                        'top_k': 50,
                        'top_p': 0.95,
                        'do_sample': True,
                        'output_dir': 'runs',
                        'log_with': 'tensorboard',
                        'save_every': 5,
                        'cliprange': 0.2,
                        'cliprange_value': 0.2,
                        'vf_coef': 0.1,
                        'gamma': 1.0,
                        'lam': 0.95
                    },
                    'start_time': '2024-01-01T12:00:00+00:00',
                    'end_time': '2024-01-01T12:30:00+00:00',
                    'total_steps': 20,
                    'average_reward': 0.75,
                    'final_reward': 0.8,
                    'status': 'completed',
                    'error': None,
                    'step_rewards': [0.6, 0.7, 0.8, 0.9]
                },
                {
                    'run_id': 'run_2',
                    'model_name': 'test/model2',
                    'template_path': 'test/template2.yaml',
                    'config': {
                        'model_name': 'test/model2',
                        'template_path': 'test/template2.yaml',
                        'learning_rate': 2e-5,
                        'batch_size': 32,
                        'mini_batch_size': 4,
                        'ppo_epochs': 4,
                        'max_steps': 50,
                        'gradient_accumulation_steps': 1,
                        'max_new_tokens': 50,
                        'temperature': 0.7,
                        'top_k': 50,
                        'top_p': 0.95,
                        'do_sample': True,
                        'output_dir': 'runs',
                        'log_with': 'tensorboard',
                        'save_every': 5,
                        'cliprange': 0.2,
                        'cliprange_value': 0.2,
                        'vf_coef': 0.1,
                        'gamma': 1.0,
                        'lam': 0.95
                    },
                    'start_time': '2024-01-01T13:00:00+00:00',
                    'end_time': None,
                    'total_steps': 25,
                    'average_reward': 0.65,
                    'final_reward': 0.7,
                    'status': 'running',
                    'error': None,
                    'step_rewards': [0.5, 0.6, 0.7, 0.8]
                }
            ]
        }
        mock_yaml_load.return_value = mock_ledger_data
        
        # Call function
        runs = load_training_ledger("test_runs")
        
        # Verify file operations
        mock_exists.assert_called_once_with("test_runs/training_ledger.yaml")
        mock_file.assert_called_once_with("test_runs/training_ledger.yaml", 'r')
        mock_yaml_load.assert_called_once()
        
        # Verify results
        assert len(runs) == 2
        assert all(isinstance(run, TrainingRun) for run in runs)
        
        # Check first run
        run1 = runs[0]
        assert run1.run_id == 'run_1'
        assert run1.model_name == 'test/model1'
        assert run1.template_path == 'test/template1.yaml'
        assert run1.status == 'completed'
        assert run1.total_steps == 20
        assert run1.average_reward == 0.75
        assert run1.final_reward == 0.8
        assert run1.step_rewards == [0.6, 0.7, 0.8, 0.9]
        
        # Check second run
        run2 = runs[1]
        assert run2.run_id == 'run_2'
        assert run2.model_name == 'test/model2'
        assert run2.status == 'running'
        assert run2.end_time is None
    
    @patch('os.path.exists')
    def test_load_training_ledger_file_not_exists(self, mock_exists):
        """Test loading ledger when file doesn't exist."""
        mock_exists.return_value = False
        
        runs = load_training_ledger("nonexistent_dir")
        
        mock_exists.assert_called_once_with("nonexistent_dir/training_ledger.yaml")
        assert runs == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_empty_file(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger from empty file."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = None  # Empty YAML file
        
        # Should raise AttributeError when trying to call .get() on None
        with pytest.raises(AttributeError):
            load_training_ledger("test_runs")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_no_runs_key(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger with no 'runs' key."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {'other_data': 'value'}  # No 'runs' key
        
        runs = load_training_ledger("test_runs")
        
        assert runs == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_empty_runs(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger with empty runs list."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {'runs': []}  # Empty runs list
        
        runs = load_training_ledger("test_runs")
        
        assert runs == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_default_output_dir(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger with default output directory."""
        mock_exists.return_value = False
        
        runs = load_training_ledger()  # No output_dir specified
        
        mock_exists.assert_called_once_with("runs/training_ledger.yaml")  # Default
        assert runs == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_yaml_error(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger when YAML parsing fails."""
        mock_exists.return_value = True
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        
        with pytest.raises(yaml.YAMLError):
            load_training_ledger("test_runs")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_training_ledger_file_read_error(self, mock_exists, mock_file):
        """Test loading ledger when file reading fails."""
        mock_exists.return_value = True
        mock_file.side_effect = IOError("File read error")
        
        with pytest.raises(IOError):
            load_training_ledger("test_runs")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    def test_load_training_ledger_malformed_run_data(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading ledger with malformed run data."""
        mock_exists.return_value = True
        mock_ledger_data = {
            'runs': [
                {
                    'run_id': 'valid_run',
                    'model_name': 'test/model',
                    'template_path': 'test/template.yaml',
                    'config': {
                        'model_name': 'test/model',
                        'template_path': 'test/template.yaml',
                        'learning_rate': 1e-5,
                        'batch_size': 16,
                        'mini_batch_size': 4,
                        'ppo_epochs': 4,
                        'max_steps': 20,
                        'gradient_accumulation_steps': 1,
                        'max_new_tokens': 50,
                        'temperature': 0.7,
                        'top_k': 50,
                        'top_p': 0.95,
                        'do_sample': True,
                        'output_dir': 'runs',
                        'log_with': 'tensorboard',
                        'save_every': 5,
                        'cliprange': 0.2,
                        'cliprange_value': 0.2,
                        'vf_coef': 0.1,
                        'gamma': 1.0,
                        'lam': 0.95
                    },
                    'start_time': '2024-01-01T12:00:00+00:00'
                },
                {
                    'run_id': 'malformed_run',
                    # Missing required fields
                }
            ]
        }
        mock_yaml_load.return_value = mock_ledger_data
        
        # Should raise error when trying to create TrainingRun from malformed data
        with pytest.raises((TypeError, KeyError)):
            load_training_ledger("test_runs")


class TestTrainingUtilityFunctionsIntegration:
    """Test integration scenarios for training utility functions."""
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_and_load_ledger_integration(self, mock_trainer_class):
        """Test integration between train_model and load_training_ledger."""
        # Setup train_model mock
        mock_trainer_instance = Mock()
        mock_trainer_instance.train.return_value = {
            "status": "success",
            "run_id": "integration_test_run",
            "total_steps": 10,
            "average_reward": 0.8,
            "final_reward": 0.85
        }
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Call train_model
        train_result = train_model(
            model_name="integration/model",
            template_path="integration/template.yaml",
            max_steps=10,
            output_dir="integration_runs"
        )
        
        # Verify training result
        assert train_result["status"] == "success"
        assert train_result["run_id"] == "integration_test_run"
        
        # Now test that load_training_ledger would work with the same output_dir
        with patch('os.path.exists', return_value=False):
            runs = load_training_ledger("integration_runs")
            assert runs == []  # No ledger file exists yet
    
    def test_utility_functions_parameter_consistency(self):
        """Test that utility functions handle parameters consistently."""
        # Test that train_model creates config with same defaults as TrainingConfig
        with patch('clarity.trainer.ClarityTrainer') as mock_trainer_class:
            mock_trainer_instance = Mock()
            mock_trainer_instance.train.return_value = {"status": "success"}
            mock_trainer_class.return_value = mock_trainer_instance
            
            # Call train_model with minimal parameters
            train_model("test/model", "test/template.yaml")
            
            # Get the config that was created
            config_arg = mock_trainer_class.call_args[0][0]
            
            # Create a default TrainingConfig for comparison
            default_config = TrainingConfig()
            
            # Verify key defaults match
            assert config_arg.learning_rate == default_config.learning_rate
            assert config_arg.batch_size == default_config.batch_size
            assert config_arg.max_steps == default_config.max_steps
            assert config_arg.temperature == default_config.temperature
            assert config_arg.output_dir == default_config.output_dir
    
    @patch('clarity.trainer.ClarityTrainer')
    def test_train_model_error_propagation(self, mock_trainer_class):
        """Test that train_model properly propagates different types of errors."""
        # Test configuration error
        mock_trainer_class.side_effect = ValueError("Invalid configuration")
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            train_model("test/model", "test/template.yaml")
        
        # Reset mock for next test
        mock_trainer_class.side_effect = None
        mock_trainer_instance = Mock()
        mock_trainer_class.return_value = mock_trainer_instance
        
        # Test training error
        mock_trainer_instance.train.side_effect = RuntimeError("Training runtime error")
        
        with pytest.raises(RuntimeError, match="Training runtime error"):
            train_model("test/model", "test/template.yaml")
    
    def test_load_training_ledger_path_handling(self):
        """Test that load_training_ledger handles different path formats correctly."""
        test_cases = [
            ("runs", "runs/training_ledger.yaml"),
            ("custom_runs", "custom_runs/training_ledger.yaml"),
            ("path/with/subdirs", "path/with/subdirs/training_ledger.yaml"),
            ("", "training_ledger.yaml"),
        ]
        
        for output_dir, expected_path in test_cases:
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                runs = load_training_ledger(output_dir)
                
                mock_exists.assert_called_once_with(expected_path)
                assert runs == []
    
    def test_utility_functions_type_safety(self):
        """Test that utility functions handle type safety correctly."""
        # Test train_model with various parameter types
        with patch('clarity.trainer.ClarityTrainer') as mock_trainer_class:
            mock_trainer_instance = Mock()
            mock_trainer_instance.train.return_value = {"status": "success"}
            mock_trainer_class.return_value = mock_trainer_instance
            
            # Test with string parameters
            train_model("string_model", "string_template.yaml")
            config = mock_trainer_class.call_args[0][0]
            assert isinstance(config.model_name, str)
            assert isinstance(config.template_path, str)
            
            # Test with numeric parameters
            train_model(
                "test/model", 
                "test/template.yaml",
                max_steps=100,
                learning_rate=1e-4,
                batch_size=32
            )
            config = mock_trainer_class.call_args[0][0]
            assert isinstance(config.max_steps, int)
            assert isinstance(config.learning_rate, float)
            assert isinstance(config.batch_size, int)