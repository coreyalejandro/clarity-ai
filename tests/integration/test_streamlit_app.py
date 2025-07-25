"""
Integration tests for the Streamlit application.

These tests verify the functionality of the Streamlit UI components
and workflows by mocking the Streamlit context and simulating user interactions.
"""

import os
import sys
import pytest
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Add the root directory to the path so we can import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the app module
import app
from clarity.scorer import Template


@pytest.fixture
def mock_streamlit():
    """Mock the streamlit module for testing."""
    with patch('app.st') as mock_st:
        # Mock session state
        mock_st.session_state = {}
        mock_st.session_state.scores_history = []
        mock_st.session_state.current_template = None
        mock_st.session_state.sample_texts = [
            "Python is a helpful programming language for beginners",
            "I don't understand this at all"
        ]
        
        # Mock common streamlit functions
        mock_st.text_area.return_value = "Test text for scoring"
        mock_st.selectbox.return_value = mock_st.session_state.sample_texts[0]
        mock_st.radio.return_value = "Use Default Template"
        mock_st.button.return_value = True
        
        # Mock columns
        col_mock = MagicMock()
        mock_st.columns.return_value = [col_mock, col_mock, col_mock]
        
        yield mock_st


@pytest.fixture
def default_template():
    """Create a default template for testing."""
    template = Template("test_template")
    template.description = "Test template for integration tests"
    template.add_rule("contains_phrase", 1.0, phrase="helpful")
    template.add_rule("word_count", 1.0, min_words=3, max_words=50)
    return template


class TestStreamlitApp:
    """Test the Streamlit application functionality."""
    
    def test_create_default_template(self):
        """Test the default template creation function."""
        yaml_text = app.create_default_template()
        
        # Parse the YAML to verify it's valid
        data = yaml.safe_load(yaml_text)
        
        assert data['name'] == 'default_template'
        assert 'description' in data
        assert 'rules' in data
        assert len(data['rules']) > 0
        
        # Verify at least one rule of each type
        rule_types = [rule['type'] for rule in data['rules']]
        assert 'contains_phrase' in rule_types
        assert 'word_count' in rule_types
    
    def test_parse_template_yaml(self):
        """Test parsing YAML into a Template object."""
        yaml_text = """
        name: test_template
        description: A test template
        rules:
          - type: contains_phrase
            weight: 2.0
            params:
              phrase: "helpful"
          - type: word_count
            weight: 1.0
            params:
              min_words: 5
              max_words: 20
        """
        
        template, error = app.parse_template_yaml(yaml_text)
        
        assert error is None
        assert template is not None
        assert template.name == "test_template"
        assert template.description == "A test template"
        assert len(template.rules) == 2
        assert template.rules[0].rule_type == "contains_phrase"
        assert template.rules[0].weight == 2.0
        assert template.rules[0].params['phrase'] == "helpful"
    
    def test_parse_template_yaml_error(self):
        """Test error handling when parsing invalid YAML."""
        yaml_text = """
        name: invalid
        description: Invalid YAML
        rules:
          - type: contains_phrase
            weight: not_a_number
        """
        
        template, error = app.parse_template_yaml(yaml_text)
        
        assert template is None
        assert error is not None
        assert "not_a_number" in error.lower()
    
    def test_score_text_with_template(self, default_template):
        """Test scoring text with a template."""
        text = "Python is a helpful programming language"
        
        result, error = app.score_text_with_template(text, default_template)
        
        assert error is None
        assert result is not None
        assert 'total_score' in result
        assert result['total_score'] == 1.0  # Both rules should pass
        assert 'rule_scores' in result
        assert len(result['rule_scores']) == 2
    
    def test_create_score_chart(self):
        """Test creating a score chart from history."""
        scores_history = [
            {'score': 0.5, 'text': 'Test 1', 'timestamp': '2025-07-19T12:00:00'},
            {'score': 0.8, 'text': 'Test 2', 'timestamp': '2025-07-19T12:01:00'},
        ]
        
        chart = app.create_score_chart(scores_history)
        
        assert chart is not None
    
    @patch('app.parse_template_yaml')
    @patch('app.score_text_with_template')
    def test_main_function_with_scoring(self, mock_score, mock_parse, mock_streamlit, default_template):
        """Test the main function with text scoring workflow."""
        # Setup mocks
        mock_parse.return_value = (default_template, None)
        mock_score.return_value = ({
            'total_score': 0.75,
            'total_weight': 2.0,
            'rule_scores': [
                {
                    'rule_type': 'contains_phrase',
                    'weight': 1.0,
                    'raw_score': 1.0,
                    'weighted_score': 1.0,
                    'params': {'phrase': 'helpful'}
                },
                {
                    'rule_type': 'word_count',
                    'weight': 1.0,
                    'raw_score': 0.5,
                    'weighted_score': 0.5,
                    'params': {'min_words': 3, 'max_words': 50}
                }
            ]
        }, None)
        
        # Set session state
        mock_streamlit.session_state.current_template = default_template
        
        # Run the main function
        app.main()
        
        # Verify the template was loaded
        assert mock_parse.called
        
        # Verify scoring was performed
        assert mock_score.called
        
        # Verify UI elements were created
        assert mock_streamlit.title.called
        assert mock_streamlit.header.called
        assert mock_streamlit.button.called
    
    def test_template_file_operations(self, mock_streamlit, default_template):
        """Test template file operations (save/load)."""
        # Create a temporary template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            default_template.to_yaml(f.name)
            yaml_path = f.name
        
        try:
            # Load the template back
            loaded_template = Template.from_yaml(yaml_path)
            
            # Verify template was loaded correctly
            assert loaded_template.name == default_template.name
            assert loaded_template.description == default_template.description
            assert len(loaded_template.rules) == len(default_template.rules)
            
            # Test that both templates give same score
            test_text = "Python is a helpful language for beginners"
            assert default_template.evaluate(test_text) == loaded_template.evaluate(test_text)
            
        finally:
            # Clean up
            os.unlink(yaml_path)