"""
Unit tests for ClarityTrainer class in ClarityAI.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime, timezone

from clarity.trainer import ClarityTrainer, TrainingConfig, TrainingRun


class TestClarityTrainerInitialization:
    """Test ClarityTrainer initialization and setup."""
    
    def test_trainer_initialization_default_config(self):
        """Test trainer initialization with default config."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        assert trainer.config == config
        assert trainer.template is None
        assert trainer.model is None
        assert trainer.tokenizer is None
        assert trainer.current_run is None
        assert trainer.logger is not None
    
    def test_trainer_initialization_custom_config(self):
        """Test trainer initialization with custom config."""
        config = TrainingConfig(
            model_name="custom/model",
            template_path="custom/template.yaml",
            learning_rate=2e-5,
            batch_size=32,
            output_dir="custom_runs"
        )
        trainer = ClarityTrainer(config)
        
        assert trainer.config == config
        assert trainer.config.model_name == "custom/model"
        assert trainer.config.learning_rate == 2e-5
        assert trainer.config.batch_size == 32
        assert trainer.config.output_dir == "custom_runs"
    
    @patch('os.makedirs')
    def test_trainer_creates_output_directory(self, mock_makedirs):
        """Test that trainer creates output directory on initialization."""
        config = TrainingConfig(output_dir="test_output")
        trainer = ClarityTrainer(config)
        
        mock_makedirs.assert_called_once_with("test_output", exist_ok=True)
    
    @patch('logging.basicConfig')
    @patch('logging.getLogger')
    def test_trainer_sets_up_logging(self, mock_get_logger, mock_basic_config):
        """Test that trainer sets up logging correctly."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        mock_basic_config.assert_called_once()
        mock_get_logger.assert_called_once_with('clarity.trainer')
        assert trainer.logger == mock_logger


class TestClarityTrainerTemplateLoading:
    """Test template loading functionality."""
    
    @patch('clarity.trainer.Template.from_yaml')
    @patch('os.path.exists')
    def test_load_template_success(self, mock_exists, mock_from_yaml):
        """Test successful template loading."""
        # Setup mocks
        mock_exists.return_value = True
        mock_template = Mock()
        mock_template.name = "test_template"
        mock_from_yaml.return_value = mock_template
        
        config = TrainingConfig(template_path="test/template.yaml")
        trainer = ClarityTrainer(config)
        
        # Load template
        result = trainer.load_template()
        
        # Verify
        mock_exists.assert_called_once_with("test/template.yaml")
        mock_from_yaml.assert_called_once_with("test/template.yaml")
        assert trainer.template == mock_template
        assert result == mock_template
    
    @patch('os.path.exists')
    def test_load_template_file_not_found(self, mock_exists):
        """Test template loading when file doesn't exist."""
        mock_exists.return_value = False
        
        config = TrainingConfig(template_path="nonexistent/template.yaml")
        trainer = ClarityTrainer(config)
        
        with pytest.raises(FileNotFoundError, match="Template not found"):
            trainer.load_template()
    
    @patch('clarity.trainer.Template.from_yaml')
    @patch('os.path.exists')
    def test_load_template_yaml_error(self, mock_exists, mock_from_yaml):
        """Test template loading when YAML parsing fails."""
        mock_exists.return_value = True
        mock_from_yaml.side_effect = yaml.YAMLError("Invalid YAML")
        
        config = TrainingConfig(template_path="invalid/template.yaml")
        trainer = ClarityTrainer(config)
        
        with pytest.raises(yaml.YAMLError):
            trainer.load_template()


class TestClarityTrainerModelLoading:
    """Test model loading functionality."""
    
    @patch('clarity.trainer.AutoModelForCausalLM.from_pretrained')
    @patch('clarity.trainer.AutoTokenizer.from_pretrained')
    def test_load_model_success(self, mock_tokenizer, mock_model):
        """Test successful model loading."""
        # Setup mocks
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = None
        mock_tokenizer_instance.eos_token = "<eos>"
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model.return_value = mock_model_instance
        
        config = TrainingConfig(model_name="test/model")
        trainer = ClarityTrainer(config)
        
        # Load model
        trainer.load_model()
        
        # Verify tokenizer loading
        mock_tokenizer.assert_called_once_with("test/model")
        assert trainer.tokenizer == mock_tokenizer_instance
        assert mock_tokenizer_instance.pad_token == "<eos>"  # Should set pad_token to eos_token
        
        # Verify model loading - don't check torch_dtype since it's imported from torch
        mock_model.assert_called_once_with("test/model", torch_dtype=mock_model.call_args[1]['torch_dtype'])
        mock_model_instance.to.assert_called_once_with("cpu")
        assert trainer.model == mock_model_instance
    
    @patch('clarity.trainer.AutoModelForCausalLM.from_pretrained')
    @patch('clarity.trainer.AutoTokenizer.from_pretrained')
    def test_load_model_tokenizer_with_existing_pad_token(self, mock_tokenizer, mock_model):
        """Test model loading when tokenizer already has pad_token."""
        # Setup mocks
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = "<pad>"  # Already has pad token
        mock_tokenizer_instance.eos_token = "<eos>"
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model.return_value = mock_model_instance
        
        config = TrainingConfig(model_name="test/model")
        trainer = ClarityTrainer(config)
        
        # Load model
        trainer.load_model()
        
        # Verify pad_token is not changed
        assert trainer.tokenizer.pad_token == "<pad>"
    
    @patch('clarity.trainer.AutoTokenizer.from_pretrained')
    def test_load_model_tokenizer_error(self, mock_tokenizer):
        """Test model loading when tokenizer loading fails."""
        mock_tokenizer.side_effect = Exception("Tokenizer loading failed")
        
        config = TrainingConfig(model_name="invalid/model")
        trainer = ClarityTrainer(config)
        
        with pytest.raises(Exception, match="Tokenizer loading failed"):
            trainer.load_model()
    
    @patch('clarity.trainer.AutoModelForCausalLM.from_pretrained')
    @patch('clarity.trainer.AutoTokenizer.from_pretrained')
    def test_load_model_model_error(self, mock_tokenizer, mock_model):
        """Test model loading when model loading fails."""
        mock_tokenizer.return_value = Mock()
        mock_model.side_effect = Exception("Model loading failed")
        
        config = TrainingConfig(model_name="invalid/model")
        trainer = ClarityTrainer(config)
        
        with pytest.raises(Exception, match="Model loading failed"):
            trainer.load_model()


class TestClarityTrainerSetup:
    """Test trainer setup functionality."""
    
    @patch('clarity.trainer.torch.optim.Adam')
    def test_setup_trainer(self, mock_adam):
        """Test trainer setup creates optimizer."""
        mock_optimizer = Mock()
        mock_adam.return_value = mock_optimizer
        
        config = TrainingConfig(learning_rate=2e-5)
        trainer = ClarityTrainer(config)
        trainer.model = Mock()  # Mock model for optimizer
        
        trainer.setup_trainer()
        
        mock_adam.assert_called_once_with(trainer.model.parameters(), lr=2e-5)
        assert trainer.optimizer == mock_optimizer
    
    def test_setup_trainer_without_model(self):
        """Test trainer setup fails without model."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        # Don't set trainer.model
        
        with pytest.raises(AttributeError):
            trainer.setup_trainer()


class TestClarityTrainerPromptGeneration:
    """Test prompt generation functionality."""
    
    def test_create_prompts_default_batch_size(self):
        """Test prompt creation with default batch size."""
        config = TrainingConfig(batch_size=4)
        trainer = ClarityTrainer(config)
        
        prompts = trainer.create_prompts()
        
        assert len(prompts) == 4
        assert all(isinstance(prompt, str) for prompt in prompts)
        assert all(len(prompt) > 0 for prompt in prompts)
    
    def test_create_prompts_custom_count(self):
        """Test prompt creation with custom count."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        prompts = trainer.create_prompts(num_prompts=6)
        
        assert len(prompts) == 6
        assert all(isinstance(prompt, str) for prompt in prompts)
    
    def test_create_prompts_cycling(self):
        """Test that prompts cycle through base prompts."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        # Get more prompts than base prompts available
        prompts = trainer.create_prompts(num_prompts=10)
        
        assert len(prompts) == 10
        # Should cycle through base prompts
        assert prompts[0] == prompts[8]  # Should cycle back (8 base prompts)
    
    def test_create_prompts_zero_count(self):
        """Test prompt creation with zero count."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        prompts = trainer.create_prompts(num_prompts=0)
        
        assert len(prompts) == 0
        assert prompts == []


class TestClarityTrainerResponseGeneration:
    """Test response generation functionality."""
    
    def test_generate_responses_success(self):
        """Test successful response generation."""
        config = TrainingConfig(
            max_new_tokens=50,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            do_sample=True
        )
        trainer = ClarityTrainer(config)
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        # Mock tensor-like inputs structure: inputs[0] should be indexable
        mock_input_tensor = MagicMock()
        mock_input_tensor.__len__.return_value = 3  # Length of input tokens
        mock_inputs = MagicMock()
        mock_inputs.__getitem__.return_value = mock_input_tensor
        mock_tokenizer.encode.return_value = mock_inputs
        mock_tokenizer.decode.return_value = "Generated response"
        mock_tokenizer.pad_token_id = 0
        mock_tokenizer.eos_token_id = 1
        trainer.tokenizer = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_outputs = MagicMock()
        # Mock the tensor indexing: outputs[0][len(inputs[0]):]
        mock_output_tensor = MagicMock()
        mock_output_tensor.__getitem__.return_value = [4, 5]  # Generated tokens after prompt
        mock_outputs.__getitem__.return_value = mock_output_tensor
        mock_model.generate.return_value = [mock_outputs]
        trainer.model = mock_model
        
        prompts = ["Test prompt 1", "Test prompt 2"]
        responses = trainer.generate_responses(prompts)
        
        assert len(responses) == 2
        assert all(response == "Generated response" for response in responses)
        
        # Verify model.generate was called with correct parameters
        assert mock_model.generate.call_count == 2
        call_args = mock_model.generate.call_args
        assert call_args[1]['max_new_tokens'] == 50
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['top_k'] == 50
        assert call_args[1]['top_p'] == 0.95
        assert call_args[1]['do_sample'] is True
    
    def test_generate_responses_empty_prompts(self):
        """Test response generation with empty prompts list."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        trainer.tokenizer = Mock()
        trainer.model = Mock()
        
        responses = trainer.generate_responses([])
        
        assert responses == []
    
    def test_generate_responses_tokenizer_error(self):
        """Test response generation when tokenizer fails."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        mock_tokenizer = Mock()
        mock_tokenizer.encode.side_effect = Exception("Tokenizer error")
        trainer.tokenizer = mock_tokenizer
        trainer.model = Mock()
        
        with pytest.raises(Exception, match="Tokenizer error"):
            trainer.generate_responses(["Test prompt"])
    
    def test_generate_responses_model_error(self):
        """Test response generation when model fails."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        mock_tokenizer = Mock()
        mock_tokenizer.encode.return_value = [1, 2, 3]
        trainer.tokenizer = mock_tokenizer
        
        mock_model = Mock()
        mock_model.generate.side_effect = Exception("Model generation error")
        trainer.model = mock_model
        
        with pytest.raises(Exception, match="Model generation error"):
            trainer.generate_responses(["Test prompt"])


class TestClarityTrainerRewardComputation:
    """Test reward computation functionality."""
    
    def test_compute_rewards_success(self):
        """Test successful reward computation."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        # Mock template
        mock_template = Mock()
        mock_template.evaluate.side_effect = [0.8, 0.6, 0.9]  # Different scores
        trainer.template = mock_template
        
        responses = ["Good response", "Average response", "Excellent response"]
        rewards = trainer.compute_rewards(responses)
        
        assert rewards == [0.8, 0.6, 0.9]
        assert mock_template.evaluate.call_count == 3
    
    def test_compute_rewards_empty_responses(self):
        """Test reward computation with empty responses."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        trainer.template = Mock()
        
        rewards = trainer.compute_rewards([])
        
        assert rewards == []
    
    def test_compute_rewards_template_error(self):
        """Test reward computation when template evaluation fails."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        mock_template = Mock()
        mock_template.evaluate.side_effect = [0.8, Exception("Evaluation error"), 0.9]
        trainer.template = mock_template
        
        responses = ["Good response", "Error response", "Excellent response"]
        rewards = trainer.compute_rewards(responses)
        
        # Should handle error gracefully and return 0.0 for failed evaluation
        assert rewards == [0.8, 0.0, 0.9]
    
    def test_compute_rewards_no_template(self):
        """Test reward computation without template."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        trainer.template = None
        
        # Should handle gracefully and return 0.0 for all responses
        rewards = trainer.compute_rewards(["Test response"])
        assert rewards == [0.0]


class TestClarityTrainerRunManagement:
    """Test training run management functionality."""
    
    @patch('clarity.trainer.datetime')
    def test_start_training_run(self, mock_datetime):
        """Test starting a training run."""
        # Mock datetime
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000"
        mock_now_utc = Mock()
        mock_now_utc.isoformat.return_value = "2024-01-01T12:00:00+00:00"
        mock_datetime.now.side_effect = [mock_now, mock_now_utc]
        mock_datetime.timezone.utc = timezone.utc
        
        config = TrainingConfig(
            model_name="test/model",
            template_path="test/template.yaml"
        )
        trainer = ClarityTrainer(config)
        
        run_id = trainer.start_training_run()
        
        assert run_id == "run_20240101_120000"
        assert trainer.current_run is not None
        assert trainer.current_run.run_id == "run_20240101_120000"
        assert trainer.current_run.model_name == "test/model"
        assert trainer.current_run.template_path == "test/template.yaml"
        assert trainer.current_run.config == config
        assert trainer.current_run.start_time == "2024-01-01T12:00:00+00:00"
        assert trainer.current_run.status == "running"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('clarity.trainer.datetime')
    def test_save_training_run_new_ledger(self, mock_datetime, mock_yaml_dump, mock_yaml_load, mock_exists, mock_file):
        """Test saving training run to new ledger."""
        # Mock datetime
        mock_now_utc = Mock()
        mock_now_utc.isoformat.return_value = "2024-01-01T13:00:00+00:00"
        mock_datetime.now.return_value = mock_now_utc
        mock_datetime.timezone.utc = timezone.utc
        
        # Mock file operations
        mock_exists.return_value = False  # No existing ledger
        
        config = TrainingConfig(output_dir="test_runs")
        trainer = ClarityTrainer(config)
        
        # Create a mock training run
        trainer.current_run = TrainingRun(
            run_id="test_run",
            model_name="test/model",
            template_path="test/template.yaml",
            config=config,
            start_time="2024-01-01T12:00:00+00:00"
        )
        trainer.current_run.step_rewards = [0.5, 0.7, 0.8]
        
        trainer.save_training_run()
        
        # Verify run was updated
        assert trainer.current_run.end_time == "2024-01-01T13:00:00+00:00"
        assert trainer.current_run.status == "completed"
        assert trainer.current_run.average_reward == 0.6666666666666666  # (0.5+0.7+0.8)/3
        assert trainer.current_run.final_reward == 0.8
        
        # Verify file operations
        mock_yaml_dump.assert_called_once()
        ledger_data = mock_yaml_dump.call_args[0][0]
        assert 'runs' in ledger_data
        assert len(ledger_data['runs']) == 1
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('clarity.trainer.datetime')
    def test_save_training_run_existing_ledger(self, mock_datetime, mock_yaml_dump, mock_yaml_load, mock_exists, mock_file):
        """Test saving training run to existing ledger."""
        # Mock datetime
        mock_now_utc = Mock()
        mock_now_utc.isoformat.return_value = "2024-01-01T13:00:00+00:00"
        mock_datetime.now.return_value = mock_now_utc
        mock_datetime.timezone.utc = timezone.utc
        
        # Mock file operations
        mock_exists.return_value = True  # Existing ledger
        mock_yaml_load.return_value = {'runs': [{'existing': 'run'}]}
        
        config = TrainingConfig(output_dir="test_runs")
        trainer = ClarityTrainer(config)
        
        # Create a mock training run
        trainer.current_run = TrainingRun(
            run_id="test_run",
            model_name="test/model",
            template_path="test/template.yaml",
            config=config,
            start_time="2024-01-01T12:00:00+00:00"
        )
        trainer.current_run.step_rewards = [0.9]
        
        trainer.save_training_run()
        
        # Verify file operations
        mock_yaml_dump.assert_called_once()
        ledger_data = mock_yaml_dump.call_args[0][0]
        assert len(ledger_data['runs']) == 2  # Existing + new run
    
    def test_save_training_run_no_current_run(self):
        """Test saving training run when no current run exists."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        trainer.current_run = None
        
        # Should return early without error
        trainer.save_training_run()
        # No assertions needed - just verify it doesn't crash
    
    @patch('clarity.trainer.datetime')
    def test_save_training_run_no_step_rewards(self, mock_datetime):
        """Test saving training run with no step rewards."""
        # Mock datetime
        mock_now_utc = Mock()
        mock_now_utc.isoformat.return_value = "2024-01-01T13:00:00+00:00"
        mock_datetime.now.return_value = mock_now_utc
        mock_datetime.timezone.utc = timezone.utc
        
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        # Create a mock training run with no step rewards
        trainer.current_run = TrainingRun(
            run_id="test_run",
            model_name="test/model",
            template_path="test/template.yaml",
            config=config,
            start_time="2024-01-01T12:00:00+00:00"
        )
        # Don't set step_rewards or set empty list
        trainer.current_run.step_rewards = []
        
        with patch('builtins.open', mock_open()), \
             patch('os.path.exists', return_value=False), \
             patch('yaml.dump'):
            trainer.save_training_run()
        
        # Should handle empty rewards gracefully
        assert trainer.current_run.average_reward == 0.0
        assert trainer.current_run.final_reward == 0.0


class TestClarityTrainerIntegration:
    """Test ClarityTrainer integration scenarios."""
    
    @patch('clarity.trainer.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('clarity.trainer.datetime')
    def test_full_training_workflow_mock(self, mock_datetime, mock_yaml_dump, mock_yaml_load, 
                                        mock_exists, mock_file, mock_makedirs):
        """Test full training workflow with mocked dependencies."""
        # Mock datetime
        mock_now = Mock()
        mock_now.strftime.return_value = "20240101_120000"
        mock_now_utc = Mock()
        mock_now_utc.isoformat.return_value = "2024-01-01T12:00:00+00:00"
        mock_datetime.now.side_effect = [mock_now, mock_now_utc, mock_now_utc]
        mock_datetime.timezone.utc = timezone.utc
        
        # Mock file operations
        mock_exists.side_effect = [True, False]  # Template exists, ledger doesn't
        mock_yaml_load.return_value = None
        
        config = TrainingConfig(
            model_name="test/model",
            template_path="test/template.yaml",
            max_steps=2,
            batch_size=2
        )
        
        with patch.object(ClarityTrainer, 'load_template') as mock_load_template, \
             patch.object(ClarityTrainer, 'load_model') as mock_load_model, \
             patch.object(ClarityTrainer, 'setup_trainer') as mock_setup_trainer, \
             patch.object(ClarityTrainer, 'create_prompts') as mock_create_prompts, \
             patch.object(ClarityTrainer, 'generate_responses') as mock_generate_responses, \
             patch.object(ClarityTrainer, 'compute_rewards') as mock_compute_rewards:
            
            # Setup method mocks
            mock_create_prompts.return_value = ["prompt1", "prompt2"]
            mock_generate_responses.return_value = ["response1", "response2"]
            mock_compute_rewards.return_value = [0.8, 0.6]
            
            trainer = ClarityTrainer(config)
            
            # Mock model saving
            trainer.model = Mock()
            trainer.tokenizer = Mock()
            
            result = trainer.train()
            
            # Verify method calls
            mock_load_template.assert_called_once()
            mock_load_model.assert_called_once()
            mock_setup_trainer.assert_called_once()
            assert mock_create_prompts.call_count == 2  # max_steps
            assert mock_generate_responses.call_count == 2
            assert mock_compute_rewards.call_count == 2
            
            # Verify result
            assert result["status"] == "success"
            assert result["run_id"] == "run_20240101_120000"
            assert result["total_steps"] == 2
    
    def test_training_error_handling(self):
        """Test training error handling."""
        config = TrainingConfig()
        trainer = ClarityTrainer(config)
        
        # Mock load_template to raise an error
        with patch.object(trainer, 'load_template', side_effect=Exception("Template error")):
            result = trainer.train()
            
            assert result["status"] == "error"
            assert "Template error" in result["error"]
    
    def test_trainer_with_realistic_config(self):
        """Test trainer initialization with realistic configuration."""
        config = TrainingConfig(
            model_name="microsoft/DialoGPT-small",
            template_path="templates/helpfulness.yaml",
            learning_rate=1e-5,
            batch_size=8,
            max_steps=10,
            temperature=0.8,
            max_new_tokens=75,
            output_dir="training_runs",
            save_every=5
        )
        
        trainer = ClarityTrainer(config)
        
        assert trainer.config.model_name == "microsoft/DialoGPT-small"
        assert trainer.config.learning_rate == 1e-5
        assert trainer.config.batch_size == 8
        assert trainer.config.max_steps == 10
        assert trainer.config.save_every == 5