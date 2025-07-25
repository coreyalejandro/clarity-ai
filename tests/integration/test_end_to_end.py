"""
Integration tests for end-to-end ClarityAI workflows.

These tests verify that all components work together correctly in realistic scenarios,
using real file operations and CLI command execution.
"""

import pytest
import tempfile
import os
import subprocess
import yaml
import json
from pathlib import Path
from unittest.mock import patch, Mock

from clarity.scorer import Template, score, score_detailed
from clarity.cli import main
from clarity.trainer import (
    TrainingConfig, 
    TrainingRun, 
    ClarityTrainer, 
    train_model, 
    load_training_ledger
)


class TestScoringWorkflow:
    """Test complete scoring workflow from template creation to result validation."""
    
    def test_template_creation_and_scoring_workflow(self):
        """Test complete workflow: create template, save to file, load and score text."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create a template programmatically
            template = Template("integration_test")
            template.description = "Integration test template for scoring workflow"
            template.add_rule("contains_phrase", 2.0, phrase="excellent")
            template.add_rule("word_count", 1.0, min_words=10, max_words=100)
            template.add_rule("sentiment_positive", 1.5)
            
            # Step 2: Save template to file
            template_path = os.path.join(temp_dir, "test_template.yaml")
            template.to_yaml(template_path)
            
            # Verify template file was created and has correct content
            assert os.path.exists(template_path)
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            assert template_data['name'] == "integration_test"
            assert template_data['description'] == "Integration test template for scoring workflow"
            assert len(template_data['rules']) == 3
            
            # Step 3: Create test text file
            text_content = "This is an excellent example of high-quality content that demonstrates positive sentiment and meets the word count requirements."
            text_path = os.path.join(temp_dir, "test_text.txt")
            with open(text_path, 'w') as f:
                f.write(text_content)
            
            # Step 4: Score text using the scorer module directly
            score_result = score(text_content, template_path)
            assert isinstance(score_result, float)
            assert score_result > 0  # Should have positive score due to "excellent" and positive sentiment
            
            # Step 5: Get detailed scoring results
            detailed_result = score_detailed(text_content, template_path)
            assert isinstance(detailed_result, dict)
            assert 'total_score' in detailed_result
            assert 'total_weight' in detailed_result
            assert 'rule_scores' in detailed_result
            assert len(detailed_result['rule_scores']) == 3
            
            # Verify rule scores
            rule_types = [rule['rule_type'] for rule in detailed_result['rule_scores']]
            assert 'contains_phrase' in rule_types
            assert 'word_count' in rule_types
            assert 'sentiment_positive' in rule_types
    
    def test_cli_scoring_integration(self):
        """Test CLI scoring commands with real file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template file
            template_data = {
                'name': 'cli_test',
                'description': 'CLI integration test template',
                'rules': [
                    {
                        'type': 'contains_phrase',
                        'weight': 1.0,
                        'params': {'phrase': 'testing'}
                    },
                    {
                        'type': 'word_count',
                        'weight': 1.0,
                        'params': {'min_words': 5, 'max_words': 50}
                    }
                ]
            }
            
            template_path = os.path.join(temp_dir, "cli_template.yaml")
            with open(template_path, 'w') as f:
                yaml.dump(template_data, f)
            
            # Create text file
            text_content = "This is a testing example with sufficient words for validation."
            text_path = os.path.join(temp_dir, "cli_text.txt")
            with open(text_path, 'w') as f:
                f.write(text_content)
            
            # Test CLI scoring with text file
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score', text_path,
                '--template', template_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            assert "Score:" in result.stdout
            
            # Test CLI scoring with direct text input
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score',
                '--text', text_content,
                '--template', template_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            assert "Score:" in result.stdout
            
            # Test CLI scoring with detailed output
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score',
                '--text', text_content,
                '--template', template_path,
                '--detailed'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            assert "Overall Score:" in result.stdout
            assert "Rule Breakdown:" in result.stdout
            assert "contains_phrase" in result.stdout
            assert "word_count" in result.stdout
    
    def test_template_creation_cli_integration(self):
        """Test CLI template creation and subsequent usage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, "created_template.yaml")
            
            # Create template using CLI
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'create-template',
                '--name', 'cli_created',
                '--description', 'Template created via CLI',
                '--output', template_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            assert "Template created:" in result.stdout
            assert os.path.exists(template_path)
            
            # Verify template content
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)
            
            assert template_data['name'] == 'cli_created'
            assert template_data['description'] == 'Template created via CLI'
            assert 'rules' in template_data
            assert len(template_data['rules']) >= 2  # Should have example rules
            
            # Use the created template for scoring
            test_text = "This is an example text with sufficient content for testing."
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score',
                '--text', test_text,
                '--template', template_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 0
            assert "Score:" in result.stdout
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with non-existent template file
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score',
                '--text', 'test text',
                '--template', 'nonexistent.yaml'
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 1
            assert "Template file not found" in result.stdout
            
            # Test with non-existent text file
            template_path = os.path.join(temp_dir, "test_template.yaml")
            template_data = {
                'name': 'error_test',
                'description': 'Error handling test',
                'rules': [{'type': 'word_count', 'weight': 1.0, 'params': {'min_words': 1}}]
            }
            with open(template_path, 'w') as f:
                yaml.dump(template_data, f)
            
            result = subprocess.run([
                'python', '-m', 'clarity.cli', 'score', 'nonexistent.txt',
                '--template', template_path
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            assert result.returncode == 1
            assert "Text file not found" in result.stdout
    
    def test_complex_template_scoring_workflow(self):
        """Test workflow with complex template containing multiple rule types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create complex template
            template = Template("complex_test")
            template.description = "Complex template with multiple rule types"
            template.add_rule("contains_phrase", 2.0, phrase="innovation")
            template.add_rule("word_count", 1.0, min_words=20, max_words=200)
            template.add_rule("sentiment_positive", 1.5)
            template.add_rule("regex_match", 1.0, pattern=r"\b\w+ing\b")  # Words ending in 'ing'
            
            template_path = os.path.join(temp_dir, "complex_template.yaml")
            template.to_yaml(template_path)
            
            # Test with text that should match all rules
            positive_text = """
            Innovation is driving technological advancement in amazing ways. 
            Companies are developing cutting-edge solutions that are transforming 
            industries and creating exciting opportunities for growth and collaboration.
            This positive trend is continuing to accelerate across multiple sectors.
            """
            
            detailed_result = score_detailed(positive_text.strip(), template_path)
            
            # Verify all rules were evaluated
            assert len(detailed_result['rule_scores']) == 4
            rule_types = [rule['rule_type'] for rule in detailed_result['rule_scores']]
            expected_types = ['contains_phrase', 'word_count', 'sentiment_positive', 'regex_match']
            for expected_type in expected_types:
                assert expected_type in rule_types
            
            # Verify positive scoring
            assert detailed_result['total_score'] > 0
            
            # Test with text that should score poorly
            negative_text = "Bad."
            
            negative_result = score_detailed(negative_text, template_path)
            assert negative_result['total_score'] < detailed_result['total_score']


class TestFileOperations:
    """Test file I/O operations in integration scenarios."""
    
    def test_template_file_formats(self):
        """Test template loading and saving with various file formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template
            template = Template("format_test")
            template.description = "Testing file format handling"
            template.add_rule("word_count", 1.0, min_words=5)
            
            # Test YAML format
            yaml_path = os.path.join(temp_dir, "template.yaml")
            template.to_yaml(yaml_path)
            
            # Load and verify
            loaded_template = Template.from_yaml(yaml_path)
            assert loaded_template.name == "format_test"
            assert loaded_template.description == "Testing file format handling"
            assert len(loaded_template.rules) == 1
            
            # Test scoring with loaded template
            test_text = "This is a test with enough words."
            score_result = loaded_template.evaluate(test_text)
            assert isinstance(score_result, float)
            assert score_result > 0
    
    def test_concurrent_file_operations(self):
        """Test handling of concurrent file operations."""
        import threading
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, "concurrent_template.yaml")
            
            # Create template
            template = Template("concurrent_test")
            template.add_rule("word_count", 1.0, min_words=1)
            template.to_yaml(template_path)
            
            results = []
            errors = []
            
            def score_text(text, thread_id):
                try:
                    result = score(f"Thread {thread_id} test text with content", template_path)
                    results.append((thread_id, result))
                except Exception as e:
                    errors.append((thread_id, str(e)))
            
            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=score_text, args=(f"test text {i}", i))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 5
            for thread_id, result in results:
                assert isinstance(result, float)
                assert result >= 0

class TestTrainingWorkflow:
    """Test complete training workflow from template loading to model saving."""
    
    def test_training_config_creation_and_serialization(self):
        """Test training configuration creation and serialization."""
        config = TrainingConfig(
            model_name="microsoft/DialoGPT-small",
            template_path="test_template.yaml",
            max_steps=5,
            learning_rate=1e-5,
            batch_size=4
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
    
    def test_training_run_metadata_management(self):
        """Test training run creation and metadata management."""
        config = TrainingConfig(max_steps=3)
        
        run = TrainingRun(
            run_id="test_run_001",
            model_name="test/model",
            template_path="test.yaml",
            config=config,
            start_time="2024-01-01T00:00:00Z"
        )
        
        # Test initial state
        assert run.run_id == "test_run_001"
        assert run.status == "running"
        assert run.step_rewards == []
        
        # Test adding rewards
        run.step_rewards = [0.1, 0.2, 0.3]
        run.total_steps = 3
        
        # Test serialization
        run_dict = run.to_dict()
        assert run_dict['run_id'] == "test_run_001"
        assert run_dict['step_rewards'] == [0.1, 0.2, 0.3]
        
        # Test deserialization
        restored_run = TrainingRun.from_dict(run_dict)
        assert restored_run.run_id == run.run_id
        assert restored_run.step_rewards == run.step_rewards
    
    @pytest.mark.slow
    def test_complete_training_pipeline(self):
        """Test complete training pipeline with mocked model operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("training_test")
            template.description = "Template for training integration test"
            template.add_rule("contains_phrase", 1.0, phrase="helpful")
            template.add_rule("word_count", 1.0, min_words=5, max_words=50)
            
            template_path = os.path.join(temp_dir, "training_template.yaml")
            template.to_yaml(template_path)
            
            # Create training config
            config = TrainingConfig(
                model_name="microsoft/DialoGPT-small",
                template_path=template_path,
                max_steps=3,
                batch_size=2,
                output_dir=temp_dir,
                save_every=2
            )
            
            # Mock the heavy model operations to avoid downloading models
            with patch('clarity.trainer.AutoTokenizer') as mock_tokenizer_class, \
                 patch('clarity.trainer.AutoModelForCausalLM') as mock_model_class:
                
                # Setup mocks
                mock_tokenizer = Mock()
                mock_tokenizer.pad_token = None
                mock_tokenizer.eos_token = "<eos>"
                mock_tokenizer.pad_token_id = 0
                mock_tokenizer.eos_token_id = 1
                mock_tokenizer.encode.return_value = [[1, 2, 3]]
                mock_tokenizer.decode.return_value = "helpful response with good content"
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.parameters.return_value = [Mock()]
                mock_model.generate.return_value = [[1, 2, 3, 4, 5, 6]]
                mock_model.to.return_value = mock_model
                mock_model_class.from_pretrained.return_value = mock_model
                
                # Run training
                trainer = ClarityTrainer(config)
                result = trainer.train()
                
                # Verify training completed successfully
                assert result['status'] == 'success'
                assert 'run_id' in result
                assert result['total_steps'] == 3
                assert 'average_reward' in result
                assert 'final_reward' in result
                
                # Verify output directory structure
                run_dir = result['output_dir']
                assert os.path.exists(run_dir)
                
                # Verify final model directory
                final_dir = os.path.join(run_dir, "final")
                assert os.path.exists(final_dir)
                
                # Verify checkpoint was saved (save_every=2, so checkpoint at step 2)
                checkpoint_dir = os.path.join(run_dir, "checkpoint-2")
                assert os.path.exists(checkpoint_dir)
                
                # Verify training ledger was created
                ledger_path = os.path.join(temp_dir, "training_ledger.yaml")
                assert os.path.exists(ledger_path)
                
                # Verify ledger content
                with open(ledger_path, 'r') as f:
                    ledger = yaml.safe_load(f)
                
                assert 'runs' in ledger
                assert len(ledger['runs']) == 1
                
                run_data = ledger['runs'][0]
                assert run_data['run_id'] == result['run_id']
                assert run_data['status'] == 'completed'
                assert run_data['total_steps'] == 3
                assert len(run_data['step_rewards']) == 3
    
    def test_training_error_handling(self):
        """Test training error handling and recovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with non-existent template
            config = TrainingConfig(
                template_path="nonexistent.yaml",
                output_dir=temp_dir,
                max_steps=1
            )
            
            trainer = ClarityTrainer(config)
            result = trainer.train()
            
            # Verify error handling
            assert result['status'] == 'error'
            assert 'error' in result
            assert 'Template not found' in result['error'] or 'FileNotFoundError' in result['error']
            
            # Verify error was logged to ledger
            ledger_path = os.path.join(temp_dir, "training_ledger.yaml")
            if os.path.exists(ledger_path):
                with open(ledger_path, 'r') as f:
                    ledger = yaml.safe_load(f)
                
                if ledger and 'runs' in ledger and ledger['runs']:
                    run_data = ledger['runs'][0]
                    assert run_data['status'] == 'failed'
                    assert 'error' in run_data
    
    def test_training_ledger_management(self):
        """Test training ledger loading and management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test empty ledger
            runs = load_training_ledger(temp_dir)
            assert runs == []
            
            # Create sample ledger data
            sample_config = TrainingConfig(max_steps=2)
            sample_run = TrainingRun(
                run_id="sample_run",
                model_name="test/model",
                template_path="test.yaml",
                config=sample_config,
                start_time="2024-01-01T00:00:00Z",
                end_time="2024-01-01T00:05:00Z",
                total_steps=2,
                average_reward=0.5,
                final_reward=0.6,
                status="completed",
                step_rewards=[0.4, 0.6]
            )
            
            # Save to ledger
            ledger_data = {'runs': [sample_run.to_dict()]}
            ledger_path = os.path.join(temp_dir, "training_ledger.yaml")
            with open(ledger_path, 'w') as f:
                yaml.dump(ledger_data, f)
            
            # Load and verify
            loaded_runs = load_training_ledger(temp_dir)
            assert len(loaded_runs) == 1
            
            loaded_run = loaded_runs[0]
            assert loaded_run.run_id == "sample_run"
            assert loaded_run.status == "completed"
            assert loaded_run.total_steps == 2
            assert loaded_run.step_rewards == [0.4, 0.6]
            assert loaded_run.config.max_steps == 2
    
    def test_train_model_convenience_function(self):
        """Test the train_model convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("convenience_test")
            template.add_rule("word_count", 1.0, min_words=1)
            
            template_path = os.path.join(temp_dir, "convenience_template.yaml")
            template.to_yaml(template_path)
            
            # Mock model operations
            with patch('clarity.trainer.AutoTokenizer') as mock_tokenizer_class, \
                 patch('clarity.trainer.AutoModelForCausalLM') as mock_model_class:
                
                # Setup mocks
                mock_tokenizer = Mock()
                mock_tokenizer.pad_token = None
                mock_tokenizer.eos_token = "<eos>"
                mock_tokenizer.pad_token_id = 0
                mock_tokenizer.eos_token_id = 1
                mock_tokenizer.encode.return_value = [[1, 2, 3]]
                mock_tokenizer.decode.return_value = "test response"
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.parameters.return_value = [Mock()]
                mock_model.generate.return_value = [[1, 2, 3, 4, 5]]
                mock_model.to.return_value = mock_model
                mock_model_class.from_pretrained.return_value = mock_model
                
                # Test convenience function
                result = train_model(
                    model_name="microsoft/DialoGPT-small",
                    template_path=template_path,
                    max_steps=2,
                    learning_rate=1e-5,
                    batch_size=2,
                    output_dir=temp_dir
                )
                
                # Verify result
                assert result['status'] == 'success'
                assert result['total_steps'] == 2
                assert 'run_id' in result
                assert 'average_reward' in result
    
    def test_cli_training_integration(self):
        """Test CLI training command integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("cli_training_test")
            template.add_rule("word_count", 1.0, min_words=1)
            
            template_path = os.path.join(temp_dir, "cli_training_template.yaml")
            template.to_yaml(template_path)
            
            # Mock the training function to avoid heavy model operations
            with patch('clarity.trainer.train_model') as mock_train:
                mock_train.return_value = {
                    'status': 'success',
                    'run_id': 'test_run_cli',
                    'total_steps': 5,
                    'average_reward': 0.7,
                    'final_reward': 0.8,
                    'output_dir': os.path.join(temp_dir, 'test_run_cli')
                }
                
                # Test CLI training command
                result = subprocess.run([
                    'python', '-m', 'clarity.cli', 'train',
                    '--template', template_path,
                    '--steps', '5',
                    '--learning-rate', '1e-5',
                    '--batch-size', '4',
                    '--output', temp_dir
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                # Verify CLI execution
                assert result.returncode == 0
                assert "Starting ClarityAI training" in result.stdout
                assert "Training completed successfully" in result.stdout
                assert "Run ID: test_run_cli" in result.stdout
                
                # Verify train_model was called with correct parameters
                mock_train.assert_called_once()
                call_args = mock_train.call_args[1]
                assert call_args['template_path'] == template_path
                assert call_args['max_steps'] == 5
                assert call_args['learning_rate'] == 1e-5
                assert call_args['batch_size'] == 4
                assert call_args['output_dir'] == temp_dir
    
    def test_training_progress_tracking(self):
        """Test training progress tracking and step rewards."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("progress_test")
            template.add_rule("contains_phrase", 1.0, phrase="good")
            
            template_path = os.path.join(temp_dir, "progress_template.yaml")
            template.to_yaml(template_path)
            
            config = TrainingConfig(
                template_path=template_path,
                max_steps=4,
                batch_size=2,
                output_dir=temp_dir
            )
            
            # Mock model operations with varying response quality
            with patch('clarity.trainer.AutoTokenizer') as mock_tokenizer_class, \
                 patch('clarity.trainer.AutoModelForCausalLM') as mock_model_class:
                
                mock_tokenizer = Mock()
                mock_tokenizer.pad_token = None
                mock_tokenizer.eos_token = "<eos>"
                mock_tokenizer.pad_token_id = 0
                mock_tokenizer.eos_token_id = 1
                mock_tokenizer.encode.return_value = [[1, 2, 3]]
                
                # Simulate improving responses over time
                responses = [
                    "bad response",  # Step 1: low score
                    "good response",  # Step 2: higher score
                    "very good response",  # Step 3: higher score
                    "excellent good response"  # Step 4: highest score
                ]
                mock_tokenizer.decode.side_effect = responses
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.parameters.return_value = [Mock()]
                mock_model.generate.return_value = [[1, 2, 3, 4, 5]]
                mock_model.to.return_value = mock_model
                mock_model_class.from_pretrained.return_value = mock_model
                
                # Run training
                trainer = ClarityTrainer(config)
                result = trainer.train()
                
                # Verify progress tracking
                assert result['status'] == 'success'
                assert len(trainer.current_run.step_rewards) == 4
                
                # Verify rewards generally improve (contains "good" phrase)
                rewards = trainer.current_run.step_rewards
                assert rewards[1] > rewards[0]  # "good response" > "bad response"
                assert rewards[3] > rewards[0]  # "excellent good response" > "bad response"

cl
ass TestTrainingWorkflow:
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
    
    @pytest.mark.skipif(
        not os.environ.get('CLARITY_FULL_INTEGRATION_TESTS'),
        reason="Full integration tests require transformers dependencies"
    )
    def test_complete_training_pipeline(self):
        """Test complete training pipeline with real model loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("training_test")
            template.description = "Training integration test template"
            template.add_rule("contains_phrase", 1.0, phrase="helpful")
            template.add_rule("word_count", 1.0, min_words=5, max_words=50)
            
            template_path = os.path.join(temp_dir, "training_template.yaml")
            template.to_yaml(template_path)
            
            # Configure training with minimal steps
            config = TrainingConfig(
                model_name="microsoft/DialoGPT-small",
                template_path=template_path,
                max_steps=2,
                batch_size=2,
                output_dir=temp_dir,
                save_every=1
            )
            
            # Run training
            trainer = ClarityTrainer(config)
            result = trainer.train()
            
            # Verify training completed
            assert result['status'] == 'success'
            assert result['total_steps'] == 2
            assert 'run_id' in result
            assert 'average_reward' in result
            assert 'final_reward' in result
            
            # Verify output directory structure
            run_dir = result['output_dir']
            assert os.path.exists(run_dir)
            assert os.path.exists(os.path.join(run_dir, 'final'))
            assert os.path.exists(os.path.join(run_dir, 'checkpoint-1'))
            assert os.path.exists(os.path.join(run_dir, 'checkpoint-2'))
            
            # Verify ledger was created
            ledger_path = os.path.join(temp_dir, 'training_ledger.yaml')
            assert os.path.exists(ledger_path)
            
            # Load and verify ledger content
            runs = load_training_ledger(temp_dir)
            assert len(runs) == 1
            assert runs[0].run_id == result['run_id']
            assert runs[0].status == 'completed'
            assert runs[0].total_steps == 2
    
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
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.to.return_value = mock_model
                mock_model.generate.return_value = [[1, 2, 3, 4, 5]]
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
            
            # Verify error was logged to ledger
            runs = load_training_ledger(temp_dir)
            assert len(runs) == 1
            assert runs[0].status == 'failed'
            assert runs[0].error is not None
    
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
                assert "Run ID: test_run_123" in result.stdout
                
                # Verify train_model was called with correct parameters
                mock_train.assert_called_once()
                call_args = mock_train.call_args[1]
                assert call_args['template_path'] == template_path
                assert call_args['max_steps'] == 5
                assert call_args['output_dir'] == temp_dir
    
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
    
    def test_training_checkpoint_management(self):
        """Test training checkpoint saving and loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template
            template = Template("checkpoint_test")
            template.add_rule("word_count", 1.0, min_words=1)
            
            template_path = os.path.join(temp_dir, "checkpoint_template.yaml")
            template.to_yaml(template_path)
            
            # Mock transformers components
            with patch('clarity.trainer.AutoTokenizer') as mock_tokenizer_class, \
                 patch('clarity.trainer.AutoModelForCausalLM') as mock_model_class:
                
                mock_tokenizer = Mock()
                mock_tokenizer.pad_token = None
                mock_tokenizer.eos_token = "<eos>"
                mock_tokenizer.save_pretrained = Mock()
                mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
                
                mock_model = Mock()
                mock_model.to.return_value = mock_model
                mock_model.save_pretrained = Mock()
                mock_model_class.from_pretrained.return_value = mock_model
                
                # Configure training with frequent checkpoints
                config = TrainingConfig(
                    model_name="test/model",
                    template_path=template_path,
                    max_steps=4,
                    output_dir=temp_dir,
                    save_every=2  # Save every 2 steps
                )
                
                # Mock the generation and scoring
                with patch.object(ClarityTrainer, 'generate_responses') as mock_gen, \
                     patch.object(ClarityTrainer, 'compute_rewards') as mock_rewards:
                    
                    mock_gen.return_value = ["test response"]
                    mock_rewards.return_value = [0.5]
                    
                    trainer = ClarityTrainer(config)
                    result = trainer.train()
                    
                    # Verify training completed
                    assert result['status'] == 'success'
                    
                    # Verify checkpoints were saved
                    # Should save at steps 2, 4, and final
                    assert mock_model.save_pretrained.call_count == 3
                    assert mock_tokenizer.save_pretrained.call_count == 3
                    
                    # Verify checkpoint directories would be created
                    expected_calls = [
                        os.path.join(temp_dir, result['run_id'], 'checkpoint-2'),
                        os.path.join(temp_dir, result['run_id'], 'checkpoint-4'),
                        os.path.join(temp_dir, result['run_id'], 'final')
                    ]
                    
                    actual_calls = [call[0][0] for call in mock_model.save_pretrained.call_args_list]
                    for expected_dir in expected_calls:
                        assert any(expected_dir in call for call in actual_calls)