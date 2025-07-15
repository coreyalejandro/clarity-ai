"""
Unit tests for Template class in ClarityAI.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open

from clarity.scorer import Template, Rule


class TestTemplate:
    """Test the base Template class functionality."""
    
    def test_template_creation_default(self):
        """Test basic template creation with default values."""
        template = Template()
        assert template.name == "default"
        assert template.description == ""
        assert template.rules == []
    
    def test_template_creation_with_name(self):
        """Test template creation with custom name."""
        template = Template("custom_template")
        assert template.name == "custom_template"
        assert template.description == ""
        assert template.rules == []
    
    def test_template_description_assignment(self):
        """Test template description assignment."""
        template = Template("test")
        template.description = "A test template for unit testing"
        assert template.description == "A test template for unit testing"


class TestTemplateRuleManagement:
    """Test template rule addition and management."""
    
    def test_add_single_rule(self):
        """Test adding a single rule to template."""
        template = Template("test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        assert len(template.rules) == 1
        assert template.rules[0].rule_type == "contains_phrase"
        assert template.rules[0].weight == 1.0
        assert template.rules[0].params == {"phrase": "test"}
    
    def test_add_multiple_rules(self):
        """Test adding multiple rules to template."""
        template = Template("multi_rule")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 2.0, min_words=5, max_words=20)
        template.add_rule("sentiment_positive", 1.5)
        
        assert len(template.rules) == 3
        
        # Check first rule
        assert template.rules[0].rule_type == "contains_phrase"
        assert template.rules[0].weight == 1.0
        assert template.rules[0].params == {"phrase": "python"}
        
        # Check second rule
        assert template.rules[1].rule_type == "word_count"
        assert template.rules[1].weight == 2.0
        assert template.rules[1].params == {"min_words": 5, "max_words": 20}
        
        # Check third rule
        assert template.rules[2].rule_type == "sentiment_positive"
        assert template.rules[2].weight == 1.5
        assert template.rules[2].params == {}
    
    def test_add_rule_with_complex_params(self):
        """Test adding rule with complex parameters."""
        template = Template("complex")
        template.add_rule(
            "regex_match", 
            2.5, 
            pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            case_sensitive=False
        )
        
        assert len(template.rules) == 1
        rule = template.rules[0]
        assert rule.rule_type == "regex_match"
        assert rule.weight == 2.5
        assert "pattern" in rule.params
        assert "case_sensitive" in rule.params
        assert rule.params["case_sensitive"] is False


class TestTemplateEvaluation:
    """Test template evaluation functionality."""
    
    def test_evaluate_empty_template(self):
        """Test evaluation of template with no rules."""
        template = Template("empty")
        assert template.evaluate("any text") == 0.0
    
    def test_evaluate_single_rule_template(self):
        """Test evaluation of template with single rule."""
        template = Template("single")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        
        # Text contains phrase
        assert template.evaluate("I love python programming") == 1.0
        
        # Text doesn't contain phrase
        assert template.evaluate("I love java programming") == 0.0
    
    def test_evaluate_multiple_rules_equal_weights(self):
        """Test evaluation with multiple rules having equal weights."""
        template = Template("equal_weights")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("contains_phrase", 1.0, phrase="programming")
        
        # Both phrases present: (1.0*1 + 1.0*1) / (1+1) = 1.0
        assert template.evaluate("python programming is fun") == 1.0
        
        # One phrase present: (1.0*1 + 0.0*1) / (1+1) = 0.5
        assert template.evaluate("python is great") == 0.5
        
        # No phrases present: (0.0*1 + 0.0*1) / (1+1) = 0.0
        assert template.evaluate("java is also good") == 0.0
    
    def test_evaluate_multiple_rules_different_weights(self):
        """Test evaluation with multiple rules having different weights."""
        template = Template("different_weights")
        template.add_rule("contains_phrase", 3.0, phrase="python")  # Higher weight
        template.add_rule("contains_phrase", 1.0, phrase="programming")  # Lower weight
        
        # Both phrases: (1.0*3 + 1.0*1) / (3+1) = 4/4 = 1.0
        assert template.evaluate("python programming rocks") == 1.0
        
        # Only high-weight phrase: (1.0*3 + 0.0*1) / (3+1) = 3/4 = 0.75
        assert template.evaluate("python is awesome") == 0.75
        
        # Only low-weight phrase: (0.0*3 + 1.0*1) / (3+1) = 1/4 = 0.25
        assert template.evaluate("programming is fun") == 0.25
    
    def test_evaluate_with_mixed_rule_types(self):
        """Test evaluation with different types of rules."""
        template = Template("mixed_types")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=3, max_words=10)
        template.add_rule("sentiment_positive", 1.0)
        
        # Text that should pass all rules
        positive_text = "python programming is excellent"  # 4 words, contains python, positive
        score = template.evaluate(positive_text)
        assert score > 0.5  # Should be high since multiple rules pass
        
        # Text that fails some rules
        negative_text = "python"  # 1 word, contains python, not positive
        score = template.evaluate(negative_text)
        assert 0.0 < score < 1.0  # Should be partial score
    
    def test_evaluate_with_zero_weights(self):
        """Test evaluation when some rules have zero weight."""
        template = Template("zero_weight")
        template.add_rule("contains_phrase", 0.0, phrase="python")
        template.add_rule("contains_phrase", 1.0, phrase="programming")
        
        # Should only consider non-zero weight rules
        assert template.evaluate("python programming") == 1.0
        assert template.evaluate("programming only") == 1.0
        assert template.evaluate("python only") == 0.0  # Zero weight rule doesn't count
    
    def test_evaluate_all_zero_weights(self):
        """Test evaluation when all rules have zero weight."""
        template = Template("all_zero")
        template.add_rule("contains_phrase", 0.0, phrase="python")
        template.add_rule("contains_phrase", 0.0, phrase="programming")
        
        # Should return 0.0 when total weight is 0
        assert template.evaluate("python programming") == 0.0


class TestTemplateDetailedEvaluation:
    """Test template detailed evaluation functionality."""
    
    def test_evaluate_detailed_empty_template(self):
        """Test detailed evaluation of empty template."""
        template = Template("empty")
        result = template.evaluate_detailed("any text")
        
        assert result["total_score"] == 0.0
        assert result["rule_scores"] == []
    
    def test_evaluate_detailed_single_rule(self):
        """Test detailed evaluation with single rule."""
        template = Template("single")
        template.add_rule("contains_phrase", 2.0, phrase="python")
        
        result = template.evaluate_detailed("python is great")
        
        assert "total_score" in result
        assert "total_weight" in result
        assert "rule_scores" in result
        
        assert result["total_score"] == 1.0
        assert result["total_weight"] == 2.0
        assert len(result["rule_scores"]) == 1
        
        rule_score = result["rule_scores"][0]
        assert rule_score["rule_type"] == "contains_phrase"
        assert rule_score["weight"] == 2.0
        assert rule_score["raw_score"] == 1.0
        assert rule_score["weighted_score"] == 2.0
        assert rule_score["params"] == {"phrase": "python"}
    
    def test_evaluate_detailed_multiple_rules(self):
        """Test detailed evaluation with multiple rules."""
        template = Template("multiple")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 2.0, min_words=2, max_words=5)
        
        result = template.evaluate_detailed("python rocks")  # 2 words, contains python
        
        assert result["total_score"] == 1.0  # Both rules pass
        assert result["total_weight"] == 3.0  # 1.0 + 2.0
        assert len(result["rule_scores"]) == 2
        
        # Check individual rule scores
        phrase_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "contains_phrase")
        word_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "word_count")
        
        assert phrase_rule["raw_score"] == 1.0
        assert phrase_rule["weighted_score"] == 1.0
        assert word_rule["raw_score"] == 1.0
        assert word_rule["weighted_score"] == 2.0
    
    def test_evaluate_detailed_with_rule_error(self):
        """Test detailed evaluation when a rule throws an error."""
        template = Template("error_test")
        template.add_rule("contains_phrase", 1.0, phrase="good")
        
        # Add a rule that will cause an error by directly manipulating the rules list
        bad_rule = Rule("unknown_type", 1.0, {})
        template.rules.append(bad_rule)
        
        result = template.evaluate_detailed("this is good text")
        
        # Should have results for both rules, one successful, one with error
        assert len(result["rule_scores"]) == 2
        
        # Find the error rule result
        error_rule = next(r for r in result["rule_scores"] if "error" in r)
        assert "error" in error_rule
        assert error_rule["rule_type"] == "unknown_type"
        assert error_rule["weight"] == 1.0
        
        # The good rule should still work
        good_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "contains_phrase")
        assert good_rule["raw_score"] == 1.0


class TestTemplateYAMLSerialization:
    """Test template YAML serialization and deserialization."""
    
    def test_to_yaml_simple_template(self):
        """Test saving simple template to YAML."""
        template = Template("simple")
        template.description = "A simple test template"
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            template.to_yaml(yaml_path)
            
            # Verify file was created and contains expected content
            assert os.path.exists(yaml_path)
            
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            
            assert data['name'] == "simple"
            assert data['description'] == "A simple test template"
            assert len(data['rules']) == 1
            assert data['rules'][0]['type'] == "contains_phrase"
            assert data['rules'][0]['weight'] == 1.0
            assert data['rules'][0]['params']['phrase'] == "test"
            
        finally:
            os.unlink(yaml_path)
    
    def test_to_yaml_complex_template(self):
        """Test saving complex template with multiple rules to YAML."""
        template = Template("complex")
        template.description = "A complex template with multiple rules"
        template.add_rule("contains_phrase", 2.0, phrase="python")
        template.add_rule("word_count", 1.5, min_words=5, max_words=20)
        template.add_rule("regex_match", 1.0, pattern=r"\d+")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            template.to_yaml(yaml_path)
            
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            
            assert data['name'] == "complex"
            assert len(data['rules']) == 3
            
            # Verify each rule
            phrase_rule = next(r for r in data['rules'] if r['type'] == 'contains_phrase')
            word_rule = next(r for r in data['rules'] if r['type'] == 'word_count')
            regex_rule = next(r for r in data['rules'] if r['type'] == 'regex_match')
            
            assert phrase_rule['weight'] == 2.0
            assert phrase_rule['params']['phrase'] == "python"
            
            assert word_rule['weight'] == 1.5
            assert word_rule['params']['min_words'] == 5
            assert word_rule['params']['max_words'] == 20
            
            assert regex_rule['weight'] == 1.0
            assert regex_rule['params']['pattern'] == r"\d+"
            
        finally:
            os.unlink(yaml_path)
    
    def test_to_yaml_creates_directory(self):
        """Test that to_yaml creates necessary directories."""
        template = Template("dir_test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml_path = os.path.join(temp_dir, "subdir", "template.yaml")
            
            # Directory doesn't exist yet
            assert not os.path.exists(os.path.dirname(yaml_path))
            
            template.to_yaml(yaml_path)
            
            # Directory should be created
            assert os.path.exists(os.path.dirname(yaml_path))
            assert os.path.exists(yaml_path)
    
    def test_from_yaml_simple_template(self):
        """Test loading simple template from YAML."""
        yaml_content = """
name: loaded_template
description: A template loaded from YAML
rules:
  - type: contains_phrase
    weight: 1.5
    params:
      phrase: "hello"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            template = Template.from_yaml(yaml_path)
            
            assert template.name == "loaded_template"
            assert template.description == "A template loaded from YAML"
            assert len(template.rules) == 1
            
            rule = template.rules[0]
            assert rule.rule_type == "contains_phrase"
            assert rule.weight == 1.5
            assert rule.params == {"phrase": "hello"}
            
        finally:
            os.unlink(yaml_path)
    
    def test_from_yaml_complex_template(self):
        """Test loading complex template from YAML."""
        yaml_content = """
name: complex_loaded
description: Complex template with multiple rules
rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "python"
  - type: word_count
    weight: 1.0
    params:
      min_words: 5
      max_words: 15
  - type: sentiment_positive
    weight: 1.5
    params: {}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            template = Template.from_yaml(yaml_path)
            
            assert template.name == "complex_loaded"
            assert len(template.rules) == 3
            
            # Test that template works correctly
            test_text = "python programming is excellent and has many good features"
            score = template.evaluate(test_text)
            assert score > 0.5  # Should score well
            
        finally:
            os.unlink(yaml_path)
    
    def test_from_yaml_with_defaults(self):
        """Test loading template with default values."""
        yaml_content = """
rules:
  - type: contains_phrase
    params:
      phrase: "test"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            template = Template.from_yaml(yaml_path)
            
            # Should use defaults
            assert template.name == "default"
            assert template.description == ""
            assert len(template.rules) == 1
            assert template.rules[0].weight == 1.0  # Default weight
            
        finally:
            os.unlink(yaml_path)
    
    def test_from_yaml_file_not_found(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError, match="Template file not found"):
            Template.from_yaml("nonexistent_file.yaml")
    
    def test_from_yaml_malformed_yaml(self):
        """Test loading from malformed YAML file."""
        malformed_content = """
name: broken
rules:
  - type: contains_phrase
    weight: invalid_weight
    params:
      phrase: "test"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(malformed_content)
            yaml_path = f.name
        
        try:
            # Should not raise an exception during loading, but might during evaluation
            template = Template.from_yaml(yaml_path)
            assert template.name == "broken"
            
        finally:
            os.unlink(yaml_path)
    
    def test_yaml_roundtrip_consistency(self):
        """Test that saving and loading a template preserves all data."""
        # Create original template
        original = Template("roundtrip_test")
        original.description = "Testing roundtrip consistency"
        original.add_rule("contains_phrase", 2.5, phrase="python")
        original.add_rule("word_count", 1.0, min_words=3, max_words=15)
        original.add_rule("sentiment_positive", 0.5)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            # Save and reload
            original.to_yaml(yaml_path)
            loaded = Template.from_yaml(yaml_path)
            
            # Verify all properties match
            assert loaded.name == original.name
            assert loaded.description == original.description
            assert len(loaded.rules) == len(original.rules)
            
            # Test that both templates give same results
            test_texts = [
                "python programming is excellent",
                "java is also good",
                "short",
                "this is a longer sentence with many words to test the word count rule"
            ]
            
            for text in test_texts:
                original_score = original.evaluate(text)
                loaded_score = loaded.evaluate(text)
                assert abs(original_score - loaded_score) < 0.001  # Allow for floating point precision
                
        finally:
            os.unlink(yaml_path)


class TestTemplateErrorHandling:
    """Test template error handling and edge cases."""
    
    def test_evaluate_with_rule_exception(self):
        """Test template evaluation when a rule throws an exception."""
        template = Template("error_handling")
        template.add_rule("contains_phrase", 1.0, phrase="good")
        
        # Add a rule that will cause an error
        bad_rule = Rule("unknown_type", 1.0, {})
        template.rules.append(bad_rule)
        
        # Should still work, just skip the bad rule
        score = template.evaluate("this is good text")
        assert score == 1.0  # Only the good rule should count
    
    def test_evaluate_all_rules_fail(self):
        """Test evaluation when all rules throw exceptions."""
        template = Template("all_fail")
        
        # Add rules that will all fail
        bad_rule1 = Rule("unknown_type1", 1.0, {})
        bad_rule2 = Rule("unknown_type2", 2.0, {})
        template.rules.extend([bad_rule1, bad_rule2])
        
        # Should return 0.0 when no rules can be evaluated
        score = template.evaluate("any text")
        assert score == 0.0
    
    def test_template_with_no_rules_edge_cases(self):
        """Test edge cases with templates that have no rules."""
        template = Template("no_rules")
        
        # Various text inputs should all return 0.0
        assert template.evaluate("") == 0.0
        assert template.evaluate("short") == 0.0
        assert template.evaluate("a very long text with many words") == 0.0
        
        # Detailed evaluation should return empty structure
        result = template.evaluate_detailed("any text")
        assert result["total_score"] == 0.0
        assert result["rule_scores"] == []


class TestTemplateIntegration:
    """Test template integration with other components."""
    
    def test_template_with_all_rule_types(self):
        """Test template that uses all available rule types."""
        template = Template("all_types")
        template.description = "Template using all rule types"
        
        # Add one of each rule type
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=5, max_words=20)
        template.add_rule("sentiment_positive", 1.0)
        template.add_rule("regex_match", 1.0, pattern=r"\d+")
        template.add_rule("cosine_sim", 1.0, target="programming language")
        
        # Test with text that should trigger multiple rules
        test_text = "python is an excellent programming language with 20 years of history"
        score = template.evaluate(test_text)
        
        # Should get a good score since multiple rules match
        assert score > 0.5
        
        # Test detailed evaluation
        detailed = template.evaluate_detailed(test_text)
        assert len(detailed["rule_scores"]) == 5
        assert detailed["total_weight"] == 5.0
    
    def test_template_performance_with_many_rules(self):
        """Test template performance with many rules."""
        template = Template("many_rules")
        
        # Add many rules
        for i in range(50):
            template.add_rule("contains_phrase", 1.0, phrase=f"word{i}")
        
        assert len(template.rules) == 50
        
        # Should still evaluate quickly
        score = template.evaluate("word25 is in this text")
        assert 0.0 < score <= 1.0  # Should find at least one match