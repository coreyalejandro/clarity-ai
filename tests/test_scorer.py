import pytest
import tempfile
import os
from clarity.scorer import Rule, Template, score, score_detailed


class TestRule:
    """Test the Rule class and all rule types."""
    
    def test_regex_match_rule(self):
        rule = Rule("regex_match", 1.0, {"pattern": r"\d+"})
        
        assert rule.evaluate("I have 5 apples") == 1.0
        assert rule.evaluate("I have no apples") == 0.0
    
    def test_contains_phrase_rule(self):
        rule = Rule("contains_phrase", 1.0, {"phrase": "hello world"})
        
        assert rule.evaluate("Hello World!") == 1.0
        assert rule.evaluate("HELLO WORLD") == 1.0
        assert rule.evaluate("goodbye world") == 0.0
    
    def test_cosine_sim_rule(self):
        rule = Rule("cosine_sim", 1.0, {"target": "machine learning python"})
        
        # Perfect overlap
        assert rule.evaluate("machine learning python") == 1.0
        
        # Partial overlap (2 out of 3 words)
        score = rule.evaluate("machine learning java")
        assert 0.6 <= score <= 0.7
        
        # No overlap
        assert rule.evaluate("cooking recipes") == 0.0
    
    def test_word_count_rule(self):
        rule = Rule("word_count", 1.0, {"min_words": 5, "max_words": 10})
        
        assert rule.evaluate("This has exactly five words") == 1.0
        assert rule.evaluate("This has ten words in total making it pass") == 1.0
        assert rule.evaluate("Too short") == 0.0
        assert rule.evaluate("This sentence is way too long and exceeds the maximum word count limit") == 0.0
    
    def test_sentiment_positive_rule(self):
        rule = Rule("sentiment_positive", 1.0, {})
        
        positive_text = "This is excellent and great work that is very helpful"
        negative_text = "This is terrible and awful"
        
        assert rule.evaluate(positive_text) > 0.5
        assert rule.evaluate(negative_text) == 0.0
    
    def test_unknown_rule_type(self):
        rule = Rule("unknown_type", 1.0, {})
        
        with pytest.raises(ValueError, match="Unknown rule type"):
            rule.evaluate("test text")


class TestTemplate:
    """Test the Template class functionality."""
    
    def test_empty_template(self):
        template = Template("empty")
        assert template.evaluate("any text") == 0.0
    
    def test_single_rule_template(self):
        template = Template("single")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        
        assert template.evaluate("I love python programming") == 1.0
        assert template.evaluate("I love java programming") == 0.0
    
    def test_multiple_rules_weighted(self):
        template = Template("multi")
        template.add_rule("contains_phrase", 2.0, phrase="python")  # weight 2
        template.add_rule("contains_phrase", 1.0, phrase="coding")  # weight 1
        
        # Text with both phrases: (1.0*2 + 1.0*1) / (2+1) = 1.0
        assert template.evaluate("python coding is fun") == 1.0
        
        # Text with only first phrase: (1.0*2 + 0.0*1) / (2+1) = 0.67
        score = template.evaluate("python is great")
        assert 0.65 <= score <= 0.69
        
        # Text with only second phrase: (0.0*2 + 1.0*1) / (2+1) = 0.33
        score = template.evaluate("coding is fun")
        assert 0.32 <= score <= 0.35
    
    def test_detailed_evaluation(self):
        template = Template("detailed")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=3, max_words=10)
        
        result = template.evaluate_detailed("python programming rocks")
        
        assert "total_score" in result
        assert "total_weight" in result
        assert "rule_scores" in result
        assert len(result["rule_scores"]) == 2
        assert result["total_weight"] == 2.0
        assert result["total_score"] == 1.0  # Both rules should pass
    
    def test_yaml_roundtrip(self):
        # Create template
        template = Template("test_template")
        template.description = "A test template"
        template.add_rule("contains_phrase", 1.0, phrase="hello")
        template.add_rule("word_count", 2.0, min_words=5, max_words=20)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            template.to_yaml(yaml_path)
            
            # Load back
            loaded_template = Template.from_yaml(yaml_path)
            
            # Verify
            assert loaded_template.name == "test_template"
            assert loaded_template.description == "A test template"
            assert len(loaded_template.rules) == 2
            
            # Test that both templates give same score
            test_text = "hello world this has enough words"
            assert template.evaluate(test_text) == loaded_template.evaluate(test_text)
            
        finally:
            os.unlink(yaml_path)
    
    def test_yaml_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Template.from_yaml("nonexistent_file.yaml")


class TestPublicAPI:
    """Test the main public functions."""
    
    def test_score_function_with_template_object(self):
        template = Template("api_test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        assert score("this is a test", template) == 1.0
        assert score("this is not", template) == 0.0
    
    def test_score_function_with_yaml_path(self):
        # Create temporary template file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
name: temp_template
description: Temporary test template
rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "success"
""")
            yaml_path = f.name
        
        try:
            assert score("this is a success story", yaml_path) == 1.0
            assert score("this is a failure", yaml_path) == 0.0
        finally:
            os.unlink(yaml_path)
    
    def test_score_detailed_function(self):
        template = Template("detailed_test")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        
        result = score_detailed("python rocks", template)
        
        assert isinstance(result, dict)
        assert "total_score" in result
        assert "rule_scores" in result
        assert result["total_score"] == 1.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_rule_evaluation_error_handling(self):
        template = Template("error_test")
        template.add_rule("contains_phrase", 1.0, phrase="good")
        
        # Add a rule that will cause an error (malformed regex)
        bad_rule = Rule("regex_match", 1.0, {"pattern": "["})  # Invalid regex
        template.rules.append(bad_rule)
        
        # Should still work, just skip the bad rule
        score = template.evaluate("this is good text")
        assert score == 1.0  # Only the good rule should count
    
    def test_zero_weight_handling(self):
        template = Template("zero_weight")
        template.add_rule("contains_phrase", 0.0, phrase="test")
        
        # Should handle zero weight gracefully
        assert template.evaluate("test text") == 0.0