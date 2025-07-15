"""
Unit tests for public scoring functions in ClarityAI.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from clarity.scorer import score, score_detailed, Template


class TestScoreFunction:
    """Test the score() public function."""
    
    def test_score_with_template_object(self):
        """Test score function with Template object input."""
        template = Template("test_template")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        
        # Test positive case
        assert score("I love python programming", template) == 1.0
        
        # Test negative case
        assert score("I love java programming", template) == 0.0
    
    def test_score_with_yaml_path(self):
        """Test score function with YAML file path input."""
        # Create temporary template file
        yaml_content = """
name: test_template
description: Test template for scoring
rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "excellent"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            # Test positive case
            assert score("This is excellent work", yaml_path) == 1.0
            
            # Test negative case
            assert score("This is poor work", yaml_path) == 0.0
            
        finally:
            os.unlink(yaml_path)
    
    def test_score_with_complex_template_object(self):
        """Test score function with complex template having multiple rules."""
        template = Template("complex")
        template.add_rule("contains_phrase", 2.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=5, max_words=15)
        template.add_rule("sentiment_positive", 1.0)
        
        # Text that should score well on all rules
        high_score_text = "python programming is excellent and very helpful"
        score_result = score(high_score_text, template)
        assert score_result > 0.7  # Should get high score
        
        # Text that should score poorly
        low_score_text = "java"  # Short, no python, not positive
        score_result = score(low_score_text, template)
        assert score_result < 0.5  # Should get low score
    
    def test_score_with_weighted_rules(self):
        """Test score function with differently weighted rules."""
        template = Template("weighted")
        template.add_rule("contains_phrase", 3.0, phrase="important")  # High weight
        template.add_rule("contains_phrase", 1.0, phrase="detail")     # Low weight
        
        # Text with high-weight phrase only: 3/(3+1) = 0.75
        score_result = score("This is important information", template)
        assert abs(score_result - 0.75) < 0.01
        
        # Text with low-weight phrase only: 1/(3+1) = 0.25
        score_result = score("This is a small detail", template)
        assert abs(score_result - 0.25) < 0.01
        
        # Text with both phrases: (3+1)/(3+1) = 1.0
        score_result = score("This important detail matters", template)
        assert score_result == 1.0
    
    def test_score_with_empty_template(self):
        """Test score function with empty template."""
        template = Template("empty")
        
        # Should return 0.0 for any text
        assert score("any text here", template) == 0.0
        assert score("", template) == 0.0
    
    def test_score_with_all_rule_types(self):
        """Test score function with template containing all rule types."""
        template = Template("all_types")
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=5, max_words=20)
        template.add_rule("sentiment_positive", 1.0)
        template.add_rule("regex_match", 1.0, pattern=r"\d+")
        template.add_rule("cosine_sim", 1.0, target="programming language")
        
        # Text that should trigger multiple rules
        test_text = "python is an excellent programming language with 10 years of history"
        score_result = score(test_text, template)
        
        # Should get a good score since multiple rules match
        assert score_result > 0.6
    
    def test_score_return_type_and_range(self):
        """Test that score function returns correct type and range."""
        template = Template("range_test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        # Test various inputs
        test_cases = [
            "test case",
            "no match here",
            "",
            "test test test multiple matches"
        ]
        
        for text in test_cases:
            result = score(text, template)
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


class TestScoreDetailedFunction:
    """Test the score_detailed() public function."""
    
    def test_score_detailed_with_template_object(self):
        """Test score_detailed function with Template object input."""
        template = Template("detailed_test")
        template.add_rule("contains_phrase", 1.5, phrase="python")
        
        result = score_detailed("python is great", template)
        
        # Check structure
        assert isinstance(result, dict)
        assert "total_score" in result
        assert "total_weight" in result
        assert "rule_scores" in result
        
        # Check values
        assert result["total_score"] == 1.0
        assert result["total_weight"] == 1.5
        assert len(result["rule_scores"]) == 1
        
        # Check rule details
        rule_detail = result["rule_scores"][0]
        assert rule_detail["rule_type"] == "contains_phrase"
        assert rule_detail["weight"] == 1.5
        assert rule_detail["raw_score"] == 1.0
        assert rule_detail["weighted_score"] == 1.5
        assert rule_detail["params"] == {"phrase": "python"}
    
    def test_score_detailed_with_yaml_path(self):
        """Test score_detailed function with YAML file path input."""
        yaml_content = """
name: detailed_yaml_test
rules:
  - type: word_count
    weight: 2.0
    params:
      min_words: 3
      max_words: 8
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "good"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            result = score_detailed("this is good work", yaml_path)  # 4 words, contains "good"
            
            assert result["total_score"] == 1.0  # Both rules should pass
            assert result["total_weight"] == 3.0  # 2.0 + 1.0
            assert len(result["rule_scores"]) == 2
            
            # Find each rule's result
            word_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "word_count")
            phrase_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "contains_phrase")
            
            assert word_rule["raw_score"] == 1.0
            assert word_rule["weighted_score"] == 2.0
            assert phrase_rule["raw_score"] == 1.0
            assert phrase_rule["weighted_score"] == 1.0
            
        finally:
            os.unlink(yaml_path)
    
    def test_score_detailed_with_multiple_rules(self):
        """Test score_detailed with multiple rules having different outcomes."""
        template = Template("multi_detailed")
        template.add_rule("contains_phrase", 1.0, phrase="python")      # Will match
        template.add_rule("contains_phrase", 1.0, phrase="java")        # Won't match
        template.add_rule("word_count", 2.0, min_words=2, max_words=5)  # Will match
        
        result = score_detailed("python rocks", template)  # 2 words, contains python
        
        # Overall score: (1*1 + 0*1 + 1*2) / (1+1+2) = 3/4 = 0.75
        assert abs(result["total_score"] - 0.75) < 0.01
        assert result["total_weight"] == 4.0
        assert len(result["rule_scores"]) == 3
        
        # Check individual rule results
        python_rule = next(r for r in result["rule_scores"] if r["params"].get("phrase") == "python")
        java_rule = next(r for r in result["rule_scores"] if r["params"].get("phrase") == "java")
        word_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "word_count")
        
        assert python_rule["raw_score"] == 1.0
        assert java_rule["raw_score"] == 0.0
        assert word_rule["raw_score"] == 1.0
    
    def test_score_detailed_with_empty_template(self):
        """Test score_detailed with empty template."""
        template = Template("empty_detailed")
        
        result = score_detailed("any text", template)
        
        assert result["total_score"] == 0.0
        assert result["rule_scores"] == []
        assert "total_weight" not in result or result.get("total_weight") == 0.0
    
    def test_score_detailed_with_rule_errors(self):
        """Test score_detailed when some rules throw errors."""
        template = Template("error_detailed")
        template.add_rule("contains_phrase", 1.0, phrase="good")
        
        # Add a rule that will cause an error
        from clarity.scorer import Rule
        bad_rule = Rule("unknown_type", 1.0, {})
        template.rules.append(bad_rule)
        
        result = score_detailed("this is good text", template)
        
        # Should have results for both rules
        assert len(result["rule_scores"]) == 2
        
        # Find the error rule result
        error_rule = next(r for r in result["rule_scores"] if "error" in r)
        good_rule = next(r for r in result["rule_scores"] if r["rule_type"] == "contains_phrase")
        
        assert "error" in error_rule
        assert error_rule["rule_type"] == "unknown_type"
        assert good_rule["raw_score"] == 1.0
    
    def test_score_detailed_comprehensive_breakdown(self):
        """Test that score_detailed provides comprehensive rule breakdown."""
        template = Template("comprehensive")
        template.add_rule("contains_phrase", 2.0, phrase="excellent")
        template.add_rule("sentiment_positive", 1.0)
        template.add_rule("word_count", 1.5, min_words=5, max_words=15)
        
        result = score_detailed("this excellent work is very good and helpful", template)
        
        # Verify all expected fields are present
        assert "total_score" in result
        assert "total_weight" in result
        assert "rule_scores" in result
        
        # Check each rule has all expected fields
        for rule_score in result["rule_scores"]:
            assert "rule_type" in rule_score
            assert "weight" in rule_score
            assert "params" in rule_score
            
            # Should have either scores or error
            if "error" not in rule_score:
                assert "raw_score" in rule_score
                assert "weighted_score" in rule_score
                assert isinstance(rule_score["raw_score"], (int, float))
                assert isinstance(rule_score["weighted_score"], (int, float))


class TestScoringFunctionEdgeCases:
    """Test edge cases and error handling for scoring functions."""
    
    def test_score_with_nonexistent_yaml_file(self):
        """Test score function with non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            score("test text", "nonexistent_file.yaml")
    
    def test_score_detailed_with_nonexistent_yaml_file(self):
        """Test score_detailed function with non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            score_detailed("test text", "nonexistent_file.yaml")
    
    def test_score_with_malformed_yaml_file(self):
        """Test score function with malformed YAML file."""
        malformed_yaml = """
name: broken
rules:
  - type: contains_phrase
    weight: "invalid_weight"
    params:
      phrase: test
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(malformed_yaml)
            yaml_path = f.name
        
        try:
            # Should load but might have issues during evaluation
            template = Template.from_yaml(yaml_path)
            result = score("test text", template)
            # Should still return a valid score (might be 0.0 due to error handling)
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
            
        finally:
            os.unlink(yaml_path)
    
    def test_score_with_empty_text(self):
        """Test scoring functions with empty text input."""
        template = Template("empty_text_test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        template.add_rule("word_count", 1.0, min_words=1, max_words=10)
        
        # Empty text should work
        score_result = score("", template)
        assert isinstance(score_result, float)
        assert score_result == 0.0  # Should fail both rules
        
        detailed_result = score_detailed("", template)
        assert isinstance(detailed_result, dict)
        assert detailed_result["total_score"] == 0.0
    
    def test_score_with_very_long_text(self):
        """Test scoring functions with very long text input."""
        template = Template("long_text_test")
        template.add_rule("contains_phrase", 1.0, phrase="needle")
        template.add_rule("word_count", 1.0, min_words=100, max_words=200)
        
        # Create very long text
        long_text = "word " * 150 + "needle " + "word " * 50  # 201 words with needle
        
        score_result = score(long_text, template)
        assert isinstance(score_result, float)
        assert 0.0 <= score_result <= 1.0
        
        detailed_result = score_detailed(long_text, template)
        assert isinstance(detailed_result, dict)
        assert "total_score" in detailed_result
    
    def test_score_with_special_characters(self):
        """Test scoring functions with text containing special characters."""
        template = Template("special_chars")
        template.add_rule("contains_phrase", 1.0, phrase="test@example.com")
        template.add_rule("regex_match", 1.0, pattern=r"\$\d+\.\d{2}")
        
        special_text = "Contact test@example.com for pricing $19.99 and more!"
        
        score_result = score(special_text, template)
        assert score_result == 1.0  # Both rules should match
        
        detailed_result = score_detailed(special_text, template)
        assert detailed_result["total_score"] == 1.0
        assert len(detailed_result["rule_scores"]) == 2
    
    def test_score_with_unicode_text(self):
        """Test scoring functions with Unicode text."""
        template = Template("unicode_test")
        template.add_rule("contains_phrase", 1.0, phrase="café")
        template.add_rule("word_count", 1.0, min_words=3, max_words=10)
        
        unicode_text = "I love café and résumé writing"
        
        score_result = score(unicode_text, template)
        assert isinstance(score_result, float)
        assert score_result > 0.0  # Should match at least the word count rule
        
        detailed_result = score_detailed(unicode_text, template)
        assert isinstance(detailed_result, dict)
    
    def test_score_functions_type_validation(self):
        """Test that scoring functions handle type validation properly."""
        template = Template("type_test")
        template.add_rule("contains_phrase", 1.0, phrase="test")
        
        # Test with valid inputs
        assert isinstance(score("test text", template), float)
        assert isinstance(score_detailed("test text", template), dict)
        
        # Test with template as string (YAML path)
        yaml_content = """
name: type_validation
rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "valid"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            assert isinstance(score("valid text", yaml_path), float)
            assert isinstance(score_detailed("valid text", yaml_path), dict)
        finally:
            os.unlink(yaml_path)


class TestScoringFunctionIntegration:
    """Test integration scenarios for scoring functions."""
    
    def test_score_consistency_between_functions(self):
        """Test that score() and score_detailed() return consistent results."""
        template = Template("consistency_test")
        template.add_rule("contains_phrase", 2.0, phrase="python")
        template.add_rule("word_count", 1.0, min_words=3, max_words=8)
        template.add_rule("sentiment_positive", 1.5)
        
        test_texts = [
            "python programming is excellent",
            "java development",
            "short",
            "this is a very long sentence with many words that exceeds the limit",
            ""
        ]
        
        for text in test_texts:
            simple_score = score(text, template)
            detailed_result = score_detailed(text, template)
            
            # Scores should match
            assert abs(simple_score - detailed_result["total_score"]) < 0.001
    
    def test_score_with_yaml_roundtrip(self):
        """Test scoring with template saved to and loaded from YAML."""
        # Create original template
        original_template = Template("roundtrip")
        original_template.description = "Roundtrip test template"
        original_template.add_rule("contains_phrase", 1.5, phrase="test")
        original_template.add_rule("word_count", 2.0, min_words=5, max_words=15)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            # Save template
            original_template.to_yaml(yaml_path)
            
            test_text = "this is a test sentence with enough words"
            
            # Score with original template
            original_score = score(test_text, original_template)
            original_detailed = score_detailed(test_text, original_template)
            
            # Score with loaded template
            loaded_score = score(test_text, yaml_path)
            loaded_detailed = score_detailed(test_text, yaml_path)
            
            # Results should be identical
            assert abs(original_score - loaded_score) < 0.001
            assert abs(original_detailed["total_score"] - loaded_detailed["total_score"]) < 0.001
            assert len(original_detailed["rule_scores"]) == len(loaded_detailed["rule_scores"])
            
        finally:
            os.unlink(yaml_path)
    
    def test_score_performance_with_complex_template(self):
        """Test scoring performance with complex templates."""
        template = Template("performance_test")
        
        # Add many rules
        for i in range(20):
            template.add_rule("contains_phrase", 1.0, phrase=f"keyword{i}")
        
        template.add_rule("word_count", 1.0, min_words=10, max_words=50)
        template.add_rule("sentiment_positive", 1.0)
        template.add_rule("regex_match", 1.0, pattern=r"\d+")
        
        # Test with various text lengths
        test_texts = [
            "short text",
            "medium length text with keyword5 and some numbers 123",
            " ".join([f"word{i}" for i in range(30)]) + " keyword10 excellent 456"
        ]
        
        for text in test_texts:
            # Should complete without errors
            score_result = score(text, template)
            detailed_result = score_detailed(text, template)
            
            assert isinstance(score_result, float)
            assert isinstance(detailed_result, dict)
            assert 0.0 <= score_result <= 1.0
            assert score_result == detailed_result["total_score"]
    
    def test_score_with_all_rule_combinations(self):
        """Test scoring with all possible rule type combinations."""
        template = Template("all_combinations")
        
        # Add all rule types with different weights
        template.add_rule("contains_phrase", 1.0, phrase="python")
        template.add_rule("word_count", 2.0, min_words=5, max_words=20)
        template.add_rule("sentiment_positive", 1.5)
        template.add_rule("regex_match", 1.0, pattern=r"v\d+\.\d+")  # version pattern
        template.add_rule("cosine_sim", 1.0, target="programming language software")
        
        # Test text that should trigger multiple rules
        test_text = "python v3.9 is an excellent programming language for software development"
        
        score_result = score(test_text, template)
        detailed_result = score_detailed(test_text, template)
        
        # Should get high score since multiple rules match
        assert score_result > 0.7
        assert score_result == detailed_result["total_score"]
        assert len(detailed_result["rule_scores"]) == 5
        
        # Verify each rule type is represented
        rule_types = {rule["rule_type"] for rule in detailed_result["rule_scores"]}
        expected_types = {"contains_phrase", "word_count", "sentiment_positive", "regex_match", "cosine_sim"}
        assert rule_types == expected_types