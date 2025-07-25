"""
Performance benchmarks for scoring operations.

These tests measure the performance of the scoring engine with various
text sizes, template complexities, and batch operations.
"""

import os
import time
import pytest
import tempfile
import random
import string
from typing import List, Dict

from clarity.scorer import Template, score, score_detailed


def generate_random_text(length: int) -> str:
    """Generate random text of specified length."""
    words = []
    word_length = 5  # Average word length
    num_words = length // (word_length + 1)  # +1 for space
    
    for _ in range(num_words):
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(
            random.randint(word_length - 2, word_length + 2)
        ))
        words.append(word)
    
    return ' '.join(words)


def create_template_with_rules(num_rules: int) -> Template:
    """Create a template with specified number of rules."""
    template = Template(f"benchmark_template_{num_rules}")
    template.description = f"Benchmark template with {num_rules} rules"
    
    # Add rules of different types
    rule_types = ["contains_phrase", "word_count", "regex_match", "sentiment_positive", "cosine_sim"]
    
    for i in range(num_rules):
        rule_type = rule_types[i % len(rule_types)]
        
        if rule_type == "contains_phrase":
            template.add_rule(rule_type, 1.0, phrase=f"word{i}")
        elif rule_type == "word_count":
            template.add_rule(rule_type, 1.0, min_words=10, max_words=1000)
        elif rule_type == "regex_match":
            template.add_rule(rule_type, 1.0, pattern=r"\b\w{5}\b")
        elif rule_type == "sentiment_positive":
            template.add_rule(rule_type, 1.0)
        elif rule_type == "cosine_sim":
            template.add_rule(rule_type, 1.0, target=f"target{i} benchmark test")
    
    return template


class TestScoringPerformance:
    """Performance benchmarks for scoring operations."""
    
    @pytest.mark.performance
    @pytest.mark.parametrize("text_length", [100, 1000, 10000])
    def test_scoring_speed_by_text_size(self, text_length):
        """Benchmark scoring speed with different text sizes."""
        # Create a simple template
        template = Template("benchmark")
        template.add_rule("contains_phrase", 1.0, phrase="benchmark")
        template.add_rule("word_count", 1.0, min_words=5, max_words=100000)
        template.add_rule("regex_match", 1.0, pattern=r"\b\w{5}\b")
        
        # Generate text of specified length
        text = generate_random_text(text_length)
        
        # Insert the benchmark word to ensure at least one rule matches
        words = text.split()
        if words:
            words[len(words) // 2] = "benchmark"
            text = ' '.join(words)
        
        # Measure scoring time
        start_time = time.time()
        result = score(text, template)
        end_time = time.time()
        
        # Calculate metrics
        elapsed_time = end_time - start_time
        chars_per_second = text_length / elapsed_time if elapsed_time > 0 else 0
        
        # Log results
        print(f"\nText length: {text_length} chars")
        print(f"Scoring time: {elapsed_time:.6f} seconds")
        print(f"Processing speed: {chars_per_second:.2f} chars/second")
        
        # Assert reasonable performance (adjust thresholds as needed)
        assert elapsed_time < text_length / 10000, f"Scoring too slow: {elapsed_time:.6f}s for {text_length} chars"
    
    @pytest.mark.performance
    @pytest.mark.parametrize("num_rules", [1, 5, 10, 20])
    def test_scoring_speed_by_template_complexity(self, num_rules):
        """Benchmark scoring speed with templates of different complexity."""
        # Create template with specified number of rules
        template = create_template_with_rules(num_rules)
        
        # Generate fixed-length text
        text_length = 1000
        text = generate_random_text(text_length)
        
        # Add some words that will match rules
        words = text.split()
        for i in range(min(num_rules, len(words))):
            if i < len(words):
                words[i] = f"word{i}"
        text = ' '.join(words)
        
        # Measure scoring time
        start_time = time.time()
        result = score(text, template)
        end_time = time.time()
        
        # Calculate metrics
        elapsed_time = end_time - start_time
        rules_per_second = num_rules / elapsed_time if elapsed_time > 0 else 0
        
        # Log results
        print(f"\nTemplate complexity: {num_rules} rules")
        print(f"Scoring time: {elapsed_time:.6f} seconds")
        print(f"Processing speed: {rules_per_second:.2f} rules/second")
        
        # Assert reasonable performance (adjust thresholds as needed)
        assert elapsed_time < 0.01 * num_rules, f"Scoring too slow: {elapsed_time:.6f}s for {num_rules} rules"
    
    @pytest.mark.performance
    @pytest.mark.parametrize("batch_size", [1, 10, 50, 100])
    def test_batch_scoring_performance(self, batch_size):
        """Benchmark batch scoring operations."""
        # Create a template
        template = Template("batch_benchmark")
        template.add_rule("contains_phrase", 1.0, phrase="benchmark")
        template.add_rule("word_count", 1.0, min_words=5, max_words=1000)
        
        # Generate batch of texts
        texts = [generate_random_text(500) for _ in range(batch_size)]
        
        # Measure batch scoring time
        start_time = time.time()
        results = [score(text, template) for text in texts]
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        avg_time_per_text = total_time / batch_size if batch_size > 0 else 0
        texts_per_second = batch_size / total_time if total_time > 0 else 0
        
        # Log results
        print(f"\nBatch size: {batch_size} texts")
        print(f"Total scoring time: {total_time:.6f} seconds")
        print(f"Average time per text: {avg_time_per_text:.6f} seconds")
        print(f"Processing speed: {texts_per_second:.2f} texts/second")
        
        # Assert reasonable performance (adjust thresholds as needed)
        assert avg_time_per_text < 0.05, f"Batch scoring too slow: {avg_time_per_text:.6f}s per text"
    
    @pytest.mark.performance
    def test_template_loading_performance(self):
        """Benchmark template loading performance."""
        # Create a complex template
        template = create_template_with_rules(20)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            template.to_yaml(f.name)
            yaml_path = f.name
        
        try:
            # Measure template loading time
            start_time = time.time()
            loaded_template = Template.from_yaml(yaml_path)
            end_time = time.time()
            
            # Calculate metrics
            loading_time = end_time - start_time
            
            # Log results
            print(f"\nTemplate loading time: {loading_time:.6f} seconds")
            print(f"Template complexity: {len(loaded_template.rules)} rules")
            
            # Assert reasonable performance
            assert loading_time < 0.1, f"Template loading too slow: {loading_time:.6f}s"
            
        finally:
            # Clean up
            os.unlink(yaml_path)
    
    @pytest.mark.performance
    def test_detailed_vs_simple_scoring(self):
        """Compare performance between detailed and simple scoring."""
        # Create a template
        template = create_template_with_rules(10)
        
        # Generate text
        text = generate_random_text(2000)
        
        # Measure simple scoring time
        start_time = time.time()
        simple_result = score(text, template)
        simple_time = time.time() - start_time
        
        # Measure detailed scoring time
        start_time = time.time()
        detailed_result = score_detailed(text, template)
        detailed_time = time.time() - start_time
        
        # Log results
        print(f"\nSimple scoring time: {simple_time:.6f} seconds")
        print(f"Detailed scoring time: {detailed_time:.6f} seconds")
        print(f"Overhead ratio: {detailed_time / simple_time if simple_time > 0 else 'N/A'}")
        
        # Assert reasonable performance
        assert detailed_time < simple_time * 2, "Detailed scoring has excessive overhead"