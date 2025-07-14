#!/usr/bin/env python3
"""
ClarityAI Demo Script

This script demonstrates ClarityAI functionality with a real language model.
Shows scoring, template usage, and model interaction.
"""

from clarity.scorer import Template, score, score_detailed
import os


def demo_basic_scoring():
    """Demo basic scoring functionality."""
    print("🎯 Demo 1: Basic Scoring")
    print("=" * 30)
    
    # Create a simple template
    template = Template("basic_demo")
    template.add_rule("contains_phrase", 2.0, phrase="python")
    template.add_rule("word_count", 1.0, min_words=5, max_words=20)
    template.add_rule("sentiment_positive", 1.0)
    
    # Test texts
    test_texts = [
        "Python is an excellent programming language for beginners",
        "Java is okay I guess",
        "I love coding in python! It's so helpful and clear.",
        "Short text",
        "This is a very long text that exceeds the maximum word count limit and should score lower because of length constraints"
    ]
    
    for i, text in enumerate(test_texts, 1):
        score_result = template.evaluate(text)
        print(f"\nText {i}: {text}")
        print(f"Score: {score_result:.3f}")


def demo_yaml_template():
    """Demo YAML template loading."""
    print("\n\n🎯 Demo 2: YAML Template")
    print("=" * 30)
    
    template_path = "templates/demo.yaml"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return
    
    # Load template from YAML
    template = Template.from_yaml(template_path)
    print(f"✓ Loaded template: {template.name}")
    print(f"Description: {template.description}")
    print(f"Rules: {len(template.rules)}")
    
    # Test with sample text
    test_text = "This is a helpful explanation about Python programming. It provides clear guidance."
    
    detailed_result = template.evaluate_detailed(test_text)
    print(f"\nTest text: {test_text}")
    print(f"Overall score: {detailed_result['total_score']:.3f}")
    print("\nRule breakdown:")
    
    for rule_score in detailed_result['rule_scores']:
        if 'error' not in rule_score:
            print(f"  {rule_score['rule_type']} (weight {rule_score['weight']}): {rule_score['raw_score']:.3f}")


def demo_model_interaction():
    """Demo with a real language model (optional - requires transformers)."""
    print("\n\n🎯 Demo 3: Real Model Interaction")
    print("=" * 30)
    
    try:
        from transformers import pipeline
        print("✓ Loading model: microsoft/DialoGPT-small")
        
        # Use a smaller, faster model for demo
        generator = pipeline('text-generation', 
                           model='microsoft/DialoGPT-small',
                           max_length=50,
                           do_sample=True,
                           temperature=0.7)
        
        # Create scoring template
        template = Template("model_demo")
        template.add_rule("contains_phrase", 1.0, phrase="helpful")
        template.add_rule("word_count", 1.0, min_words=3, max_words=30)
        
        # Generate and score responses
        prompts = [
            "How can I help you?",
            "What is programming?",
            "Explain AI briefly:"
        ]
        
        print("\nGenerating and scoring responses...")
        
        for prompt in prompts:
            try:
                # Generate response
                response = generator(prompt, max_length=40, num_return_sequences=1)[0]['generated_text']
                completion = response[len(prompt):].strip()
                
                if completion:
                    score_result = template.evaluate(completion)
                    print(f"\nPrompt: {prompt}")
                    print(f"Response: {completion}")
                    print(f"Score: {score_result:.3f}")
                else:
                    print(f"\nPrompt: {prompt}")
                    print(f"Response: [Empty]")
                    print(f"Score: 0.000")
                    
            except Exception as e:
                print(f"Error with prompt '{prompt}': {e}")
        
    except ImportError:
        print("⚠️  Transformers not installed - skipping model demo")
        print("To run this demo: pip install transformers torch")
    except Exception as e:
        print(f"❌ Error in model demo: {e}")


def main():
    """Run all demos."""
    print("🚀 ClarityAI Demo Script")
    print("========================\n")
    
    # Run all demo functions
    demo_basic_scoring()
    demo_yaml_template()
    demo_model_interaction()
    
    print("\n\n✅ Demo completed!")
    print("\nNext steps:")
    print("1. Try: python -m clarity.cli score --text 'Hello world' --template templates/demo.yaml")
    print("2. Try: python -m clarity.cli demo --model microsoft/DialoGPT-small")
    print("3. Install: pip install -e .")


if __name__ == "__main__":
    main()