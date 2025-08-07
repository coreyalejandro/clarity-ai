"""
DSPy Integration for Code Documentation Prompt Optimization
Using DSPy to find optimal prompts for different models and tasks
"""
import dspy
import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

# Configure DSPy with a local model (we'll use transformers)
class TransformersLM(dspy.LM):
    """Custom DSPy LM for using transformers models locally"""
    
    def __init__(self, model_name="gpt2"):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate(self, prompt, max_tokens=50, **kwargs):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_tokens,
                temperature=0.8,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        generated_text = self.tokenizer.decode(
            outputs[0][len(inputs[0]):], 
            skip_special_tokens=True
        )
        return [generated_text.strip()]
    
    def __call__(self, prompt, **kwargs):
        return self.generate(prompt, **kwargs)[0]

class CodeDocumentationSignature(dspy.Signature):
    """Generate high-quality code documentation"""
    
    context = dspy.InputField(desc="Code context or programming concept to document")
    documentation = dspy.OutputField(desc="Clear, helpful documentation with examples")

class CodeDocGenerator(dspy.Module):
    """DSPy module for generating code documentation"""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(CodeDocumentationSignature)
    
    def forward(self, context):
        result = self.generate(context=context)
        return result.documentation

class ClarityAIMetric:
    """Custom metric using ClarityAI scoring"""
    
    def __init__(self, template_path="templates/code_documentation.yaml"):
        self.template = Template.from_yaml(template_path)
    
    def __call__(self, example, prediction, trace=None):
        """Score the prediction using ClarityAI"""
        try:
            score = self.template.score(prediction)
            return score
        except Exception as e:
            print(f"Scoring error: {e}")
            return 0.0

def create_code_doc_examples():
    """Create training examples for DSPy optimization"""
    
    examples = [
        {
            "context": "Python function that calculates factorial",
            "expected_doc": "A function that calculates the factorial of a number using recursion. Includes proper docstring, parameter validation, and usage examples."
        },
        {
            "context": "REST API endpoint for user authentication", 
            "expected_doc": "API endpoint documentation with request/response format, authentication requirements, status codes, and curl examples."
        },
        {
            "context": "JavaScript async/await pattern",
            "expected_doc": "Clear explanation of async/await with practical examples, error handling, and best practices for asynchronous code."
        },
        {
            "context": "Database query optimization",
            "expected_doc": "Guide to optimizing SQL queries with indexing strategies, query analysis, and performance measurement examples."
        },
        {
            "context": "React component lifecycle methods",
            "expected_doc": "Comprehensive guide to React lifecycle methods with code examples, use cases, and migration to hooks."
        }
    ]
    
    # Convert to DSPy examples
    dspy_examples = []
    for ex in examples:
        dspy_examples.append(
            dspy.Example(
                context=ex["context"],
                documentation=ex["expected_doc"]
            ).with_inputs("context")
        )
    
    return dspy_examples

def optimize_code_doc_prompts():
    """Use DSPy to optimize prompts for code documentation"""
    
    print("🔧 DSPy Code Documentation Prompt Optimization")
    print("=" * 60)
    
    # Models to test
    models = ["gpt2", "distilgpt2"]  # Start with smaller models
    
    results = {}
    
    for model_name in models:
        print(f"\n🚀 Optimizing prompts for {model_name}")
        print("-" * 40)
        
        try:
            # Set up DSPy with this model
            lm = TransformersLM(model_name)
            dspy.configure(lm=lm)
            
            # Create the module
            code_doc_gen = CodeDocGenerator()
            
            # Create examples and metric
            examples = create_code_doc_examples()
            metric = ClarityAIMetric()
            
            print(f"📊 Created {len(examples)} training examples")
            
            # Split examples
            train_examples = examples[:3]  # Use fewer for speed
            dev_examples = examples[3:]
            
            print(f"🏋️ Training examples: {len(train_examples)}")
            print(f"🧪 Dev examples: {len(dev_examples)}")
            
            # Optimize with DSPy (using simple optimizer for speed)
            from dspy.teleprompt import BootstrapFewShot
            
            optimizer = BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=2,  # Keep small for speed
                max_labeled_demos=2
            )
            
            print("🔄 Running DSPy optimization...")
            optimized_gen = optimizer.compile(
                student=code_doc_gen,
                trainset=train_examples,
                valset=dev_examples
            )
            
            # Test the optimized generator
            print("🧪 Testing optimized generator...")
            test_contexts = [
                "Python error handling with try-catch",
                "Git merge conflict resolution"
            ]
            
            baseline_scores = []
            optimized_scores = []
            
            for context in test_contexts:
                # Test baseline
                baseline_result = code_doc_gen(context=context)
                baseline_score = metric(None, baseline_result)
                baseline_scores.append(baseline_score)
                
                # Test optimized
                optimized_result = optimized_gen(context=context)
                optimized_score = metric(None, optimized_result)
                optimized_scores.append(optimized_score)
                
                print(f"   Context: {context[:50]}...")
                print(f"   Baseline: {baseline_score:.3f}")
                print(f"   Optimized: {optimized_score:.3f}")
            
            avg_baseline = sum(baseline_scores) / len(baseline_scores)
            avg_optimized = sum(optimized_scores) / len(optimized_scores)
            improvement = ((avg_optimized - avg_baseline) / avg_baseline * 100) if avg_baseline > 0 else 0
            
            results[model_name] = {
                "baseline_avg": avg_baseline,
                "optimized_avg": avg_optimized,
                "improvement_pct": improvement,
                "baseline_scores": baseline_scores,
                "optimized_scores": optimized_scores
            }
            
            print(f"\n📊 Results for {model_name}:")
            print(f"   Baseline Average: {avg_baseline:.3f}")
            print(f"   Optimized Average: {avg_optimized:.3f}")
            print(f"   Improvement: {improvement:+.1f}%")
            
        except Exception as e:
            print(f"❌ Error with {model_name}: {e}")
            results[model_name] = {"error": str(e)}
    
    # Save results
    results_file = f"dspy_optimization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'experiment': 'DSPy Code Documentation Prompt Optimization',
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Summary
    print(f"\n🎯 DSPy OPTIMIZATION SUMMARY")
    print("=" * 40)
    
    successful_results = {k: v for k, v in results.items() if 'error' not in v}
    if successful_results:
        best_model = max(successful_results.items(), key=lambda x: x[1]['improvement_pct'])
        print(f"🏆 Best Model: {best_model[0]} ({best_model[1]['improvement_pct']:+.1f}%)")
        
        print(f"\n💡 KEY INSIGHTS:")
        for model_name, data in successful_results.items():
            if data['improvement_pct'] > 0:
                print(f"   ✅ {model_name}: DSPy improved prompts by {data['improvement_pct']:+.1f}%")
            else:
                print(f"   ⚠️ {model_name}: DSPy didn't improve ({data['improvement_pct']:+.1f}%)")
    else:
        print("❌ No successful optimizations")
    
    return results

def create_dspy_integration_guide():
    """Create a guide for integrating DSPy with ClarityAI"""
    
    guide = '''# DSPy + ClarityAI Integration Guide

## What This Enables

1. **Automatic Prompt Optimization**: DSPy finds better prompts for any model/task combination
2. **Multi-Model Testing**: Test prompt effectiveness across different models
3. **Custom Metrics**: Use ClarityAI scoring as the optimization target
4. **Few-Shot Learning**: Bootstrap examples to improve performance

## Key Components

### 1. Custom LM Integration
```python
class TransformersLM(dspy.LM):
    # Wraps HuggingFace models for DSPy
```

### 2. Task-Specific Signatures  
```python
class CodeDocumentationSignature(dspy.Signature):
    context = dspy.InputField(desc="Code to document")
    documentation = dspy.OutputField(desc="Clear documentation")
```

### 3. ClarityAI Metric
```python
class ClarityAIMetric:
    def __call__(self, example, prediction):
        return self.template.score(prediction)
```

## Benefits for Model Repurposing

1. **Better Prompts**: DSPy finds prompts that work better for specific models
2. **Task Adaptation**: Automatically adapt prompts when repurposing models
3. **Quality Optimization**: Use ClarityAI scoring to drive optimization
4. **Systematic Testing**: Compare prompt strategies across models

## Next Steps

1. Integrate DSPy optimization into model repurposing workflow
2. Create task-specific signatures for different skills
3. Use DSPy to find optimal few-shot examples
4. Compare DSPy-optimized vs manual prompts
'''

    with open('dspy_clarityai_integration_guide.md', 'w') as f:
        f.write(guide)
    
    print("📚 Created: dspy_clarityai_integration_guide.md")

if __name__ == "__main__":
    print("🔬 DSPy + ClarityAI Experiment")
    print("=" * 50)
    
    # Check if DSPy is available
    try:
        import dspy
        print("✅ DSPy is available")
    except ImportError:
        print("❌ DSPy not installed. Install with: pip install dspy-ai")
        print("   Continuing without DSPy optimization...")
        create_dspy_integration_guide()
        exit()
    
    # Run the optimization experiment
    results = optimize_code_doc_prompts()
    
    # Create integration guide
    create_dspy_integration_guide()
    
    print(f"\n🎉 DSPy integration complete!")
    print("Next: Use optimized prompts in model repurposing experiments")