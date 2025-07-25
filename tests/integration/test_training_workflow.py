"""
Integration tests for ClarityAI training workflow.

These tests verify that the training pipeline works correctly from template loading
to model saving, including training run creation, progress tracking, and ledger management.
"""

import pytest
import tempfile
import os
import subprocess
import yaml
import json
from pathlib import Path
from unittest.mock import patch, Mock

from clarity.scorer import Template
from clarity.trainer import (
    TrainingConfig, 
    TrainingRun, 
    ClarityTrainer, 
    train_model, 
    load_training_ledger
)


class TestTrainingWorkflow:
    """Test complete training workflow from template loading to model saving."""
    
    def test_training_config_creation_and_serialization(self):
        """Test TrainingConfig creation, serialization, and deserialization."""
        config = TrainingConfig(
            model_name="microsoft/DialoGPT-small",
            template_path="test_template.yaml",
            max_steps=5,
            learning_rate=1e-5,
            batch_size=8
        )
        
        # Test serialization
        config_dict = config.to_dict()
        assert config_dict['model_name'] == "microsoft/DialoGPT-small"
        assert config_dict['max_steps'] == 5
        assert config_dict['learning_rate'] == 1e-5
        
        # Test deserialization
        restored_config = TrainingConfig.from_dict(config_dict)
        assert restored_config.model_name == config.model_name
        assert restored_config.max_steps == config.max_steps
        assert restored_config.learning_rate == config.learning_rate
    
    def test_training_run_metadata_handling(self):
        """Test TrainingRun creation and metadata management."""
        config = TrainingConfig(max_steps=3)
        
        run = TrainingRun(
            run_id="test_run_123",
            model_name="test/model",
            template_path="test.yaml",
            config=config,
            start_time="2024-01-01T00:00:00Z"
        )
        
        # Test initial state
        assert run.run_id == "test_run_123"
        assert run.status == "running"
        assert run.step_rewards == []
        assert run.total_steps == 0
        
        # Test serialization
        run_dict = run.to_dict()
        assert 'config' in run_dict
        assert run_dict['run_id'] == "test_run_123"
        
        # Test deserialization
        restored_run = TrainingRun.from_dict(run_dict)
        assert restored_run.run_id == run.run_id
        assert restored_run.config.max_steps == config.max_steps
    
    def test_training_with_mocked_dependencies(self):
        """Test training workflow with mocked transformers dependencies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("mock_training_test")
            template.add_rule("word_count", 1.0, min_words=1)
            
            template_path = os.path.join(temp_dir, "mock_template.yaml")
            template.to_yaml(template_path)
            
            # Mock transformers components
            with patch('clarity.trainer.AutoTokenizer') as mock_tokenizer_class, \
                 patch('clarity.trainer.AutoModelForCausalLM') as mock_model_class, \
                 patch('torch.optim.Adam') as mock_optimizer:
                
                # Setup mocks
                mock_tokenizer = Mock()
                mock_tokenizer.pad_token = None
                mock_tokenizer.eos_token = "<eos>"
                mock_tokenizer.pad_token_id = 0
                mock_tokenizer.eos_token_id = 1
                mock_tokenizer.encode.return_value = [[1, 2, 3]]
                mock_tokenizer.decode.return_value = "helpful response"
                mock_tokenizer.save_pretrained = Mock()
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.to.return_value = mock_model
                mock_model.generate.return_value = [[1, 2, 3, 4, 5]]
                mock_model.save_pretrained = Mock()
                mock_model_class.from_pretrained.return_value = mock_model
                
                # Configure training
                config = TrainingConfig(
                    model_name="test/model",
                    template_path=template_path,
                    max_steps=3,
                    batch_size=2,
                    output_dir=temp_dir
                )
                
                # Run training
                trainer = ClarityTrainer(config)
                result = trainer.train()
                
                # Verify training completed
                assert result['status'] == 'success'
                assert result['total_steps'] == 3
                assert isinstance(result['average_reward'], float)
                assert isinstance(result['final_reward'], float)
                
                # Verify mocks were called
                mock_tokenizer_class.from_pretrained.assert_called_once()
                mock_model_class.from_pretrained.assert_called_once()
                mock_optimizer.assert_called_once()
    
    def test_training_error_handling(self):
        """Test training error handling and recovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with non-existent template
            config = TrainingConfig(
                template_path="nonexistent.yaml",
                output_dir=temp_dir
            )
            
            trainer = ClarityTrainer(config)
            result = trainer.train()
            
            assert result['status'] == 'error'
            assert 'Template not found' in result['error']
    
    def test_training_ledger_management(self):
        """Test training ledger creation and management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple training runs
            config1 = TrainingConfig(output_dir=temp_dir)
            config2 = TrainingConfig(output_dir=temp_dir, max_steps=5)
            
            run1 = TrainingRun(
                run_id="run_001",
                model_name="test/model1",
                template_path="template1.yaml",
                config=config1,
                start_time="2024-01-01T00:00:00Z",
                status="completed",
                total_steps=3,
                average_reward=0.75
            )
            
            run2 = TrainingRun(
                run_id="run_002", 
                model_name="test/model2",
                template_path="template2.yaml",
                config=config2,
                start_time="2024-01-02T00:00:00Z",
                status="failed",
                error="Mock error"
            )
            
            # Save runs to ledger
            ledger_path = os.path.join(temp_dir, 'training_ledger.yaml')
            ledger_data = {
                'runs': [run1.to_dict(), run2.to_dict()]
            }
            
            with open(ledger_path, 'w') as f:
                yaml.dump(ledger_data, f)
            
            # Load and verify ledger
            loaded_runs = load_training_ledger(temp_dir)
            assert len(loaded_runs) == 2
            
            # Verify first run
            assert loaded_runs[0].run_id == "run_001"
            assert loaded_runs[0].status == "completed"
            assert loaded_runs[0].total_steps == 3
            assert loaded_runs[0].average_reward == 0.75
            
            # Verify second run
            assert loaded_runs[1].run_id == "run_002"
            assert loaded_runs[1].status == "failed"
            assert loaded_runs[1].error == "Mock error"
    
    def test_cli_training_integration(self):
        """Test CLI training command integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template_data = {
                'name': 'cli_training_test',
                'description': 'CLI training integration test',
                'rules': [
                    {
                        'type': 'word_count',
                        'weight': 1.0,
                        'params': {'min_words': 1, 'max_words': 100}
                    }
                ]
            }
            
            template_path = os.path.join(temp_dir, "cli_training_template.yaml")
            with open(template_path, 'w') as f:
                yaml.dump(template_data, f)
            
            # Mock the training function to avoid actual model loading
            with patch('clarity.trainer.train_model') as mock_train:
                mock_train.return_value = {
                    "status": "success",
                    "run_id": "test_run_123",
                    "total_steps": 5,
                    "average_reward": 0.8,
                    "final_reward": 0.85,
                    "output_dir": os.path.join(temp_dir, "test_run_123")
                }
                
                # Test CLI training command
                result = subprocess.run([
                    'python', '-m', 'clarity.cli', 'train',
                    '--template', template_path,
                    '--steps', '5',
                    '--output', temp_dir
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                assert result.returncode == 0
                assert "Starting ClarityAI training" in result.stdout
                assert "Training completed successfully" in result.stdout
                assert "Run ID:" in result.stdout
                
                # Training completed successfully (actual training ran)
    
    def test_training_convenience_function(self):
        """Test the train_model convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("convenience_test")
            template.add_rule("word_count", 1.0, min_words=1)
            
            template_path = os.path.join(temp_dir, "convenience_template.yaml")
            template.to_yaml(template_path)
            
            # Mock the ClarityTrainer
            with patch('clarity.trainer.ClarityTrainer') as mock_trainer_class:
                mock_trainer = Mock()
                mock_trainer.train.return_value = {
                    "status": "success",
                    "run_id": "convenience_run",
                    "total_steps": 10,
                    "average_reward": 0.7,
                    "final_reward": 0.8,
                    "output_dir": temp_dir
                }
                mock_trainer_class.return_value = mock_trainer
                
                # Call convenience function
                result = train_model(
                    model_name="test/model",
                    template_path=template_path,
                    max_steps=10,
                    learning_rate=2e-5,
                    batch_size=8,
                    output_dir=temp_dir
                )
                
                # Verify result
                assert result['status'] == 'success'
                assert result['run_id'] == 'convenience_run'
                assert result['total_steps'] == 10
                
                # Verify trainer was created with correct config
                mock_trainer_class.assert_called_once()
                config = mock_trainer_class.call_args[0][0]
                assert config.model_name == "test/model"
                assert config.template_path == template_path
                assert config.max_steps == 10
                assert config.learning_rate == 2e-5
                assert config.batch_size == 8
                assert config.output_dir == temp_dir
    
