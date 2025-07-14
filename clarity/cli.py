#!/usr/bin/env python3
"""
ClarityAI Command Line Interface

Usage:
    clarity score <text_file> --template <template_file>
    clarity score --text "Direct text input" --template <template_file>
    clarity demo --model <model_name>
"""

import argparse
import sys
import os
from typing import Optional
import json

from .scorer import score, score_detailed, Template


def score_command(args):
    """Handle the 'clarity score' command."""
    
    # Get text input
    if args.text_file:
        if not os.path.exists(args.text_file):
            print(f"Error: Text file not found: {args.text_file}")
            return 1
        
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
    elif args.text:
        text = args.text
    else:
        print("Error: Must provide either --text-file or --text")
        return 1
    
    # Check template file exists
    if not os.path.exists(args.template):
        print(f"Error: Template file not found: {args.template}")
        return 1
    
    try:
        if args.detailed:
            result = score_detailed(text, args.template)
            print(f"Overall Score: {result['total_score']:.3f}")
            print(f"Total Weight: {result['total_weight']}")
            print("\nRule Breakdown:")
            for rule_score in result['rule_scores']:
                if 'error' in rule_score:
                    print(f"  ❌ {rule_score['rule_type']} (weight: {rule_score['weight']}): ERROR - {rule_score['error']}")
                else:
                    print(f"  ✓ {rule_score['rule_type']} (weight: {rule_score['weight']}): {rule_score['raw_score']:.3f} → {rule_score['weighted_score']:.3f}")
        else:
            result = score(text, args.template)
            print(f"Score: {result:.3f}")
        
        return 0
    
    except Exception as e:
        print(f"Error scoring text: {e}")
        return 1


def demo_command(args):
    """Handle the 'clarity demo' command."""
    
    try:
        from transformers import pipeline, AutoTokenizer
        print(f"Loading model: {args.model}")
        
        # Load the model
        generator = pipeline('text-generation', model=args.model, max_length=100, do_sample=True, temperature=0.7)
        tokenizer = AutoTokenizer.from_pretrained(args.model)
        
        print(f"✓ Model loaded successfully")
        
        # Create a simple demo template
        demo_template = Template("demo")
        demo_template.add_rule("contains_phrase", 2.0, phrase="helpful")
        demo_template.add_rule("word_count", 1.0, min_words=10, max_words=50)
        demo_template.add_rule("sentiment_positive", 1.0)
        
        # Demo prompts
        prompts = [
            "Write a helpful explanation about",
            "Provide a clear answer for",
            "Give me advice on"
        ]
        
        print("\n🚀 Demo: Generating and scoring responses...")
        print("=" * 50)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\nPrompt {i}: {prompt}")
            
            # Generate response
            try:
                response = generator(prompt, max_length=80, num_return_sequences=1)[0]['generated_text']
                # Extract just the completion (remove the prompt)
                completion = response[len(prompt):].strip()
                
                if completion:
                    print(f"Response: {completion}")
                    
                    # Score the response
                    score_result = demo_template.evaluate(completion)
                    print(f"Score: {score_result:.3f}")
                    
                    # Show detailed breakdown
                    detailed = demo_template.evaluate_detailed(completion)
                    print("Rule breakdown:")
                    for rule_score in detailed['rule_scores']:
                        if 'error' not in rule_score:
                            print(f"  {rule_score['rule_type']}: {rule_score['raw_score']:.2f}")
                else:
                    print("Response: [Empty completion]")
                    print("Score: 0.000")
            
            except Exception as e:
                print(f"Error generating response: {e}")
        
        print("\n✓ Demo completed!")
        return 0
        
    except ImportError:
        print("Error: transformers library not installed. Run: pip install transformers torch")
        return 1
    except Exception as e:
        print(f"Error running demo: {e}")
        return 1


def create_template_command(args):
    """Handle the 'clarity create-template' command."""
    
    template = Template(args.name)
    template.description = args.description or f"Template: {args.name}"
    
    # Add some example rules
    template.add_rule("contains_phrase", 1.0, phrase="example")
    template.add_rule("word_count", 1.0, min_words=5, max_words=100)
    
    try:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        template.to_yaml(args.output)
        print(f"✓ Template created: {args.output}")
        print(f"Edit the file to customize your scoring rules.")
        return 0
    except Exception as e:
        print(f"Error creating template: {e}")
        return 1


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="ClarityAI - Train LLMs with teacher-style rubrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clarity score example.txt --template rubric.yaml
  clarity score --text "Hello world" --template rubric.yaml --detailed
  clarity demo --model microsoft/DialoGPT-small
  clarity create-template --name "code-review" --output templates/code.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score text against a template')
    score_group = score_parser.add_mutually_exclusive_group(required=True)
    score_group.add_argument('text_file', nargs='?', help='Path to text file to score')
    score_group.add_argument('--text', help='Direct text input to score')
    score_parser.add_argument('--template', required=True, help='Path to YAML template file')
    score_parser.add_argument('--detailed', action='store_true', help='Show detailed rule breakdown')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run a live demo with a language model')
    demo_parser.add_argument('--model', default='microsoft/DialoGPT-small', help='HuggingFace model name (default: microsoft/DialoGPT-small)')
    
    # Create template command
    template_parser = subparsers.add_parser('create-template', help='Create a new template file')
    template_parser.add_argument('--name', required=True, help='Template name')
    template_parser.add_argument('--description', help='Template description')
    template_parser.add_argument('--output', required=True, help='Output YAML file path')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate command handler
    if args.command == 'score':
        return score_command(args)
    elif args.command == 'demo':
        return demo_command(args)
    elif args.command == 'create-template':
        return create_template_command(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())