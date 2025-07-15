"""
Unit tests for CLI command functions in ClarityAI.
"""

import pytest
import tempfile
import os
import sys
import argparse
from unittest.mock import Mock, MagicMock, patch, mock_open

# Helper function for raising exceptions in lambda functions
def raise_(ex):
    raise ex
from io import StringIO

from clarity.cli import score_command, demo_command, create_template_command, train_command, main


class TestScoreCommand:
    """Test the score_command function."""
    
    def test_score_command_with_text_file_success(self):
        """Test score command with text file input - success case."""
        # Create mock args
        args = Mock()
        args.text_file = "test.txt"
        args.text = None
        args.template = "template.yaml"
        args.detailed = False
        
        # Mock file operations and scoring
        with patch('os.path.exists', side_effect=[True, True]), \
             patch('builtins.open', mock_open(read_data="Test text content")), \
             patch('clarity.cli.score', return_value=0.85), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 0
            mock_print.assert_called_with("Score: 0.850")
    
    def test_score_command_with_direct_text_success(self):
        """Test score command with direct text input - success case."""
        args = Mock()
        args.text_file = None
        args.text = "Direct text input"
        args.template = "template.yaml"
        args.detailed = False
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.cli.score', return_value=0.75), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 0
            mock_print.assert_called_with("Score: 0.750")
    
    def test_score_command_with_detailed_output(self):
        """Test score command with detailed output."""
        args = Mock()
        args.text_file = None
        args.text = "Test text"
        args.template = "template.yaml"
        args.detailed = True
        
        mock_detailed_result = {
            'total_score': 0.8,
            'total_weight': 3.0,
            'rule_scores': [
                {
                    'rule_type': 'contains_phrase',
                    'weight': 2.0,
                    'raw_score': 1.0,
                    'weighted_score': 2.0,
                    'params': {'phrase': 'test'}
                },
                {
                    'rule_type': 'word_count',
                    'weight': 1.0,
                    'raw_score': 0.0,
                    'weighted_score': 0.0,
                    'params': {'min_words': 10}
                }
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.cli.score_detailed', return_value=mock_detailed_result), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 0
            # Verify detailed output was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert "Overall Score: 0.800" in print_calls
            assert "Total Weight: 3.0" in print_calls
            assert "\nRule Breakdown:" in print_calls
    
    def test_score_command_with_rule_error(self):
        """Test score command with rule error in detailed output."""
        args = Mock()
        args.text_file = None
        args.text = "Test text"
        args.template = "template.yaml"
        args.detailed = True
        
        mock_detailed_result = {
            'total_score': 0.5,
            'total_weight': 2.0,
            'rule_scores': [
                {
                    'rule_type': 'contains_phrase',
                    'weight': 1.0,
                    'raw_score': 1.0,
                    'weighted_score': 1.0,
                    'params': {'phrase': 'test'}
                },
                {
                    'rule_type': 'regex_match',
                    'weight': 1.0,
                    'error': 'Invalid regex pattern',
                    'params': {'pattern': '[invalid'}
                }
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.cli.score_detailed', return_value=mock_detailed_result), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 0
            # Verify error rule was displayed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            error_line = next((call for call in print_calls if "❌" in call and "ERROR" in call), None)
            assert error_line is not None
    
    def test_score_command_text_file_not_found(self):
        """Test score command when text file doesn't exist."""
        args = Mock()
        args.text_file = "nonexistent.txt"
        args.text = None
        args.template = "template.yaml"
        args.detailed = False
        
        with patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error: Text file not found: nonexistent.txt")
    
    def test_score_command_template_not_found(self):
        """Test score command when template file doesn't exist."""
        args = Mock()
        args.text_file = None
        args.text = "Test text"
        args.template = "nonexistent.yaml"
        args.detailed = False
        
        with patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error: Template file not found: nonexistent.yaml")
    
    def test_score_command_no_text_input(self):
        """Test score command when no text input is provided."""
        args = Mock()
        args.text_file = None
        args.text = None
        args.template = "template.yaml"
        args.detailed = False
        
        with patch('builtins.print') as mock_print:
            result = score_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error: Must provide either --text-file or --text")
    
    def test_score_command_scoring_error(self):
        """Test score command when scoring raises an exception."""
        args = Mock()
        args.text_file = None
        args.text = "Test text"
        args.template = "template.yaml"
        args.detailed = False
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.cli.score', side_effect=Exception("Scoring failed")), \
             patch('builtins.print') as mock_print:
            
            result = score_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error scoring text: Scoring failed")
    
    def test_score_command_file_read_error(self):
        """Test score command when file reading fails."""
        args = Mock()
        args.text_file = "test.txt"
        args.text = None
        args.template = "template.yaml"
        args.detailed = False
        
        # The file read error is not wrapped in try/except, so it will be raised
        with patch('os.path.exists', side_effect=[True, True]), \
             patch('builtins.open', side_effect=OSError("File read error")):
            
            with pytest.raises(OSError, match="File read error"):
                score_command(args)


class TestDemoCommand:
    """Test the demo_command function."""
    
    def test_demo_command_success(self):
        """Test demo command success case."""
        args = Mock()
        args.model = "test/model"
        
        # Mock the transformers imports inside the demo_command function
        with patch.dict('sys.modules', {'transformers': Mock()}):
            with patch('transformers.pipeline') as mock_pipeline, \
                 patch('transformers.AutoTokenizer') as mock_tokenizer, \
                 patch('clarity.cli.Template') as mock_template_class, \
                 patch('builtins.print') as mock_print:
                
                # Mock pipeline and tokenizer
                mock_generator = Mock()
                mock_generator.return_value = [{'generated_text': 'Write a helpful explanation about machine learning'}]
                mock_pipeline.return_value = mock_generator
                mock_tokenizer.from_pretrained.return_value = Mock()
                
                # Mock template
                mock_template = Mock()
                mock_template.evaluate.return_value = 0.75
                mock_template.evaluate_detailed.return_value = {
                    'rule_scores': [
                        {'rule_type': 'contains_phrase', 'raw_score': 1.0},
                        {'rule_type': 'word_count', 'raw_score': 0.5}
                    ]
                }
                mock_template_class.return_value = mock_template
                
                result = demo_command(args)
                
                assert result == 0
                # Verify model loading message
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                assert "Loading model: test/model" in print_calls
                assert "✓ Model loaded successfully" in print_calls
                # Check for demo completion message (it might have a newline prefix)
                assert any("✓ Demo completed!" in call for call in print_calls)
    
    def test_demo_command_with_empty_completion(self):
        """Test demo command when model generates empty completion."""
        args = Mock()
        args.model = "test/model"
        
        with patch.dict('sys.modules', {'transformers': Mock()}):
            with patch('transformers.pipeline') as mock_pipeline, \
                 patch('transformers.AutoTokenizer') as mock_tokenizer, \
                 patch('clarity.cli.Template') as mock_template_class, \
                 patch('builtins.print') as mock_print:
                
                # Mock pipeline to return prompt only (no completion)
                mock_generator = Mock()
                mock_generator.return_value = [{'generated_text': 'Write a helpful explanation about'}]  # Same as prompt
                mock_pipeline.return_value = mock_generator
                mock_tokenizer.from_pretrained.return_value = Mock()
                
                # Mock template
                mock_template = Mock()
                mock_template.evaluate.return_value = 0.0
                mock_template.evaluate_detailed.return_value = {
                    'rule_scores': [
                        {'rule_type': 'contains_phrase', 'raw_score': 0.0},
                        {'rule_type': 'word_count', 'raw_score': 0.0}
                    ]
                }
                mock_template_class.return_value = mock_template
                
                result = demo_command(args)
                
                assert result == 0
                # Verify empty completion handling
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                assert "Response: [Empty completion]" in print_calls
                assert "Score: 0.000" in print_calls
    
    def test_demo_command_generation_error(self):
        """Test demo command when text generation fails."""
        args = Mock()
        args.model = "test/model"
        
        with patch.dict('sys.modules', {'transformers': Mock()}):
            with patch('transformers.pipeline') as mock_pipeline, \
                 patch('transformers.AutoTokenizer') as mock_tokenizer, \
                 patch('clarity.cli.Template') as mock_template_class, \
                 patch('builtins.print') as mock_print:
                
                # Mock pipeline to raise error during generation
                mock_generator = Mock()
                mock_generator.side_effect = Exception("Generation failed")
                mock_pipeline.return_value = mock_generator
                mock_tokenizer.from_pretrained.return_value = Mock()
                
                # Mock template
                mock_template = Mock()
                mock_template_class.return_value = mock_template
                
                result = demo_command(args)
                
                assert result == 0  # Demo continues despite generation errors
                # Verify error handling
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                error_messages = [call for call in print_calls if "Error generating response" in call]
                assert len(error_messages) > 0
    
    def test_demo_command_import_error(self):
        """Test demo command when transformers is not installed."""
        args = Mock()
        args.model = "test/model"
        
        # Mock the import to raise ImportError
        with patch.dict('sys.modules', {'transformers': None}):
            with patch('builtins.__import__', side_effect=lambda name, *args: 
                       raise_(ImportError("No module named 'transformers'")) if name == 'transformers' else __import__(name, *args)), \
                 patch('builtins.print') as mock_print:
                
                result = demo_command(args)
                
                assert result == 1
                mock_print.assert_called_with("Error: transformers library not installed. Run: pip install transformers torch")
    
    def test_demo_command_model_loading_error(self):
        """Test demo command when model loading fails."""
        args = Mock()
        args.model = "invalid/model"
        
        with patch.dict('sys.modules', {'transformers': Mock()}):
            with patch('transformers.pipeline', side_effect=Exception("Model not found")), \
                 patch('transformers.AutoTokenizer') as mock_tokenizer, \
                 patch('builtins.print') as mock_print:
                
                result = demo_command(args)
                
                assert result == 1
                # Check that the error message contains the expected text
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                error_message = next((call for call in print_calls if "Error running demo:" in call), None)
                assert error_message is not None


class TestCreateTemplateCommand:
    """Test the create_template_command function."""
    
    def test_create_template_command_success(self):
        """Test create template command success case."""
        args = Mock()
        args.name = "test_template"
        args.description = "A test template"
        args.output = "templates/test.yaml"
        
        with patch('os.makedirs') as mock_makedirs, \
             patch('clarity.cli.Template') as mock_template_class, \
             patch('builtins.print') as mock_print:
            
            # Mock template instance
            mock_template = Mock()
            mock_template_class.return_value = mock_template
            
            result = create_template_command(args)
            
            assert result == 0
            
            # Verify template creation
            mock_template_class.assert_called_once_with("test_template")
            assert mock_template.description == "A test template"
            mock_template.add_rule.assert_any_call("contains_phrase", 1.0, phrase="example")
            mock_template.add_rule.assert_any_call("word_count", 1.0, min_words=5, max_words=100)
            mock_template.to_yaml.assert_called_once_with("templates/test.yaml")
            
            # Verify directory creation and output
            mock_makedirs.assert_called_once_with("templates", exist_ok=True)
            mock_print.assert_any_call("✓ Template created: templates/test.yaml")
    
    def test_create_template_command_no_description(self):
        """Test create template command without description."""
        args = Mock()
        args.name = "no_desc_template"
        args.description = None
        args.output = "test.yaml"
        
        with patch('os.makedirs'), \
             patch('clarity.cli.Template') as mock_template_class, \
             patch('builtins.print'):
            
            mock_template = Mock()
            mock_template_class.return_value = mock_template
            
            result = create_template_command(args)
            
            assert result == 0
            assert mock_template.description == "Template: no_desc_template"
    
    def test_create_template_command_directory_creation_error(self):
        """Test create template command when directory creation fails."""
        args = Mock()
        args.name = "test_template"
        args.description = "Test"
        args.output = "invalid/path/test.yaml"
        
        with patch('os.makedirs', side_effect=OSError("Permission denied")), \
             patch('clarity.cli.Template') as mock_template_class, \
             patch('builtins.print') as mock_print:
            
            mock_template = Mock()
            mock_template.to_yaml.side_effect = OSError("Permission denied")
            mock_template_class.return_value = mock_template
            
            result = create_template_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error creating template: Permission denied")
    
    def test_create_template_command_yaml_write_error(self):
        """Test create template command when YAML writing fails."""
        args = Mock()
        args.name = "test_template"
        args.description = "Test"
        args.output = "test.yaml"
        
        with patch('os.makedirs'), \
             patch('clarity.cli.Template') as mock_template_class, \
             patch('builtins.print') as mock_print:
            
            mock_template = Mock()
            mock_template.to_yaml.side_effect = Exception("YAML write error")
            mock_template_class.return_value = mock_template
            
            result = create_template_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error creating template: YAML write error")


class TestTrainCommand:
    """Test the train_command function."""
    
    def test_train_command_success(self):
        """Test train command success case."""
        args = Mock()
        args.model = "test/model"
        args.template = "template.yaml"
        args.steps = 50
        args.learning_rate = 2e-5
        args.batch_size = 32
        args.output = "training_runs"
        
        # Mock successful training result
        mock_train_result = {
            "status": "success",
            "run_id": "run_20240101_120000",
            "total_steps": 50,
            "average_reward": 0.75,
            "final_reward": 0.85,
            "output_dir": "training_runs/run_20240101_120000"
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.trainer.train_model', return_value=mock_train_result) as mock_train_model, \
             patch('builtins.print') as mock_print:
            
            result = train_command(args)
            
            assert result == 0
            
            # Verify train_model was called with correct parameters
            mock_train_model.assert_called_once_with(
                model_name="test/model",
                template_path="template.yaml",
                max_steps=50,
                learning_rate=2e-5,
                batch_size=32,
                output_dir="training_runs"
            )
            
            # Verify success output
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert "🚀 Starting ClarityAI training..." in print_calls
            assert "\n✅ Training completed successfully!" in print_calls
            assert "Run ID: run_20240101_120000" in print_calls
    
    def test_train_command_failure(self):
        """Test train command failure case."""
        args = Mock()
        args.model = "test/model"
        args.template = "template.yaml"
        args.steps = 10
        args.learning_rate = 1e-5
        args.batch_size = 16
        args.output = "runs"
        
        # Mock failed training result
        mock_train_result = {
            "status": "error",
            "error": "Template not found",
            "run_id": "run_20240101_120000"
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.trainer.train_model', return_value=mock_train_result), \
             patch('builtins.print') as mock_print:
            
            result = train_command(args)
            
            assert result == 1
            
            # Verify failure output
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert "\n❌ Training failed: Template not found" in print_calls
    
    def test_train_command_template_not_found(self):
        """Test train command when template file doesn't exist."""
        args = Mock()
        args.model = "test/model"
        args.template = "nonexistent.yaml"
        args.steps = 10
        args.learning_rate = 1e-5
        args.batch_size = 16
        args.output = "runs"
        
        with patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            result = train_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error: Template file not found: nonexistent.yaml")
    
    def test_train_command_import_error(self):
        """Test train command when training dependencies are missing."""
        args = Mock()
        args.model = "test/model"
        args.template = "template.yaml"
        args.steps = 10
        args.learning_rate = 1e-5
        args.batch_size = 16
        args.output = "runs"
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.trainer.train_model', side_effect=ImportError("No module named 'datasets'")), \
             patch('builtins.print') as mock_print:
            
            result = train_command(args)
            
            assert result == 1
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Missing training dependencies" in call for call in print_calls)
    
    def test_train_command_training_exception(self):
        """Test train command when training raises an exception."""
        args = Mock()
        args.model = "test/model"
        args.template = "template.yaml"
        args.steps = 10
        args.learning_rate = 1e-5
        args.batch_size = 16
        args.output = "runs"
        
        with patch('os.path.exists', return_value=True), \
             patch('clarity.trainer.train_model', side_effect=Exception("Training crashed")), \
             patch('builtins.print') as mock_print:
            
            result = train_command(args)
            
            assert result == 1
            mock_print.assert_called_with("Error during training: Training crashed")


class TestMainFunction:
    """Test the main CLI function and argument parsing."""
    
    def test_main_no_command(self):
        """Test main function when no command is provided."""
        with patch('sys.argv', ['clarity']), \
             patch('argparse.ArgumentParser.print_help') as mock_help:
            
            result = main()
            
            assert result == 1
            mock_help.assert_called_once()
    
    def test_main_score_command_routing(self):
        """Test main function routes to score command correctly."""
        test_args = [
            'clarity', 'score', '--text', 'test text', 
            '--template', 'template.yaml'
        ]
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.score_command', return_value=0) as mock_score:
            
            result = main()
            
            assert result == 0
            mock_score.assert_called_once()
            # Verify args were parsed correctly
            args = mock_score.call_args[0][0]
            assert args.text == 'test text'
            assert args.template == 'template.yaml'
    
    def test_main_demo_command_routing(self):
        """Test main function routes to demo command correctly."""
        test_args = ['clarity', 'demo', '--model', 'test/model']
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.demo_command', return_value=0) as mock_demo:
            
            result = main()
            
            assert result == 0
            mock_demo.assert_called_once()
            args = mock_demo.call_args[0][0]
            assert args.model == 'test/model'
    
    def test_main_create_template_command_routing(self):
        """Test main function routes to create-template command correctly."""
        test_args = [
            'clarity', 'create-template', '--name', 'test', 
            '--output', 'test.yaml'
        ]
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.create_template_command', return_value=0) as mock_create:
            
            result = main()
            
            assert result == 0
            mock_create.assert_called_once()
            args = mock_create.call_args[0][0]
            assert args.name == 'test'
            assert args.output == 'test.yaml'
    
    def test_main_train_command_routing(self):
        """Test main function routes to train command correctly."""
        test_args = [
            'clarity', 'train', '--model', 'test/model',
            '--template', 'template.yaml', '--steps', '100'
        ]
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.train_command', return_value=0) as mock_train:
            
            result = main()
            
            assert result == 0
            mock_train.assert_called_once()
            args = mock_train.call_args[0][0]
            assert args.model == 'test/model'
            assert args.template == 'template.yaml'
            assert args.steps == 100
    
    def test_main_unknown_command(self):
        """Test main function with unknown command."""
        test_args = ['clarity', 'unknown-command']
        
        with patch('sys.argv', test_args), \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        # argparse exits with code 2 for invalid arguments
        assert exc_info.value.code == 2
    
    def test_main_score_command_argument_validation(self):
        """Test main function validates score command arguments."""
        # Test missing required template argument
        test_args = ['clarity', 'score', '--text', 'test']
        
        with patch('sys.argv', test_args), \
             pytest.raises(SystemExit):  # argparse exits on missing required args
            main()
    
    def test_main_score_command_mutually_exclusive_args(self):
        """Test main function handles mutually exclusive arguments."""
        # Test providing both text file and direct text (should be mutually exclusive)
        test_args = [
            'clarity', 'score', 'file.txt', '--text', 'direct text',
            '--template', 'template.yaml'
        ]
        
        with patch('sys.argv', test_args), \
             pytest.raises(SystemExit):  # argparse exits on conflicting args
            main()
    
    def test_main_train_command_default_values(self):
        """Test main function uses correct default values for train command."""
        test_args = ['clarity', 'train', '--template', 'template.yaml']
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.train_command', return_value=0) as mock_train:
            
            result = main()
            
            assert result == 0
            args = mock_train.call_args[0][0]
            assert args.model == 'microsoft/DialoGPT-small'  # Default
            assert args.steps == 20  # Default
            assert args.learning_rate == 1.41e-5  # Default
            assert args.batch_size == 16  # Default
            assert args.output == 'runs'  # Default
    
    def test_main_demo_command_default_values(self):
        """Test main function uses correct default values for demo command."""
        test_args = ['clarity', 'demo']
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.demo_command', return_value=0) as mock_demo:
            
            result = main()
            
            assert result == 0
            args = mock_demo.call_args[0][0]
            assert args.model == 'microsoft/DialoGPT-small'  # Default


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_cli_error_propagation(self):
        """Test that CLI properly propagates error codes."""
        # Test that command failures result in non-zero exit codes
        test_cases = [
            (['clarity', 'score', '--text', 'test', '--template', 'nonexistent.yaml'], 1),
            (['clarity', 'train', '--template', 'nonexistent.yaml'], 1),
        ]
        
        for args, expected_code in test_cases:
            with patch('sys.argv', args), \
                 patch('os.path.exists', return_value=False), \
                 patch('builtins.print'):
                
                result = main()
                assert result == expected_code
    
    def test_cli_help_text_generation(self):
        """Test that CLI generates help text correctly."""
        with patch('sys.argv', ['clarity', '--help']), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        # argparse exits with code 0 for help
        assert exc_info.value.code == 0
        
        # Verify help text content
        help_text = mock_stdout.getvalue()
        assert "ClarityAI - Train LLMs with teacher-style rubrics" in help_text
        assert "Available commands" in help_text
        assert "Examples:" in help_text
    
    def test_cli_subcommand_help(self):
        """Test that subcommands generate help text correctly."""
        subcommands = ['score', 'demo', 'create-template', 'train']
        
        for subcommand in subcommands:
            with patch('sys.argv', ['clarity', subcommand, '--help']), \
                 patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
                 pytest.raises(SystemExit) as exc_info:
                main()
            
            # argparse exits with code 0 for help
            assert exc_info.value.code == 0
            
            # Verify subcommand help text content
            help_text = mock_stdout.getvalue()
            assert subcommand in help_text
            
            # Check for specific arguments based on subcommand
            if subcommand == 'score':
                assert "--template" in help_text
                assert "--detailed" in help_text
            elif subcommand == 'demo':
                assert "--model" in help_text
            elif subcommand == 'create-template':
                assert "--name" in help_text
                assert "--output" in help_text
            elif subcommand == 'train':
                assert "--model" in help_text
                assert "--template" in help_text
                assert "--steps" in help_text
    
    def test_cli_invalid_argument_values(self):
        """Test CLI handling of invalid argument values."""
        # Test invalid steps value (should be positive integer)
        test_args = ['clarity', 'train', '--template', 'template.yaml', '--steps', '-10']
        
        with patch('sys.argv', test_args), \
             patch('os.path.exists', return_value=True), \
             patch('clarity.cli.train_command', return_value=1) as mock_train:
            
            result = main()
            
            # Verify that the command was called with the negative value
            args = mock_train.call_args[0][0]
            assert args.steps == -10  # The CLI doesn't validate this, but the command might
    
    def test_cli_argument_type_conversion(self):
        """Test CLI argument type conversion."""
        # Test numeric argument conversion
        test_args = ['clarity', 'train', '--template', 'template.yaml', 
                    '--steps', '50', '--learning-rate', '0.0001', '--batch-size', '32']
        
        with patch('sys.argv', test_args), \
             patch('clarity.cli.train_command', return_value=0) as mock_train:
            
            result = main()
            
            assert result == 0
            args = mock_train.call_args[0][0]
            assert args.steps == 50  # Converted to int
            assert args.learning_rate == 0.0001  # Converted to float
            assert args.batch_size == 32  # Converted to int
    
    def test_cli_command_error_handling(self):
        """Test CLI error handling for unknown commands."""
        # Test with completely unknown command
        test_args = ['clarity', 'nonexistent-command']
        
        with patch('sys.argv', test_args), \
             patch('sys.stderr', new_callable=StringIO), \
             pytest.raises(SystemExit) as exc_info:
            main()
        
        # argparse exits with code 2 for unknown commands
        assert exc_info.value.code == 2