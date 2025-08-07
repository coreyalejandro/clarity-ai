"""
Experiment 2: Test different models with code documentation scoring templates
"""
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model
from fix_trainer_simple import train_model_real
import json
from datetime import datetime

def test_code_documentation_models():
    """Test different models for code documentation generation"""
    
    print("🧪 EXPERIMENT 2: Code Documentation Skill Transfer")
    print("="*60)
    
    models_to_test = [
        ("gpt2", "Standard GPT-2"),
        ("gpt2-medium", "Medium GPT-2"), 
        ("microsoft/DialoGPT-small", "DialoGPT-small"),
        ("distilgpt2", "DistilGPT2")
    ]
    
    template_path = "templates/code_documentation.yaml"
    baseline_results = {}
    
    print("📊 Step 1: Testing baseline performance with code documentation scoring")
    print("-" * 40)
    
    for model_name, display_name in models_to_test:
        print(f"\n🔬 Testing {display_name}...")
        try:
            results, avg_score = test_model(model_name, f"BASELINE-CODE-DOCS", template_path)
            baseline_results[model_name] = {
                'score': avg_score,
                'results': results,
                'display_name': display_name
            }
            print(f"   ✅ Baseline Score: {avg_score:.3f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            baseline_results[model_name] = {
                'score': 0.0,
                'error': str(e),
                'display_name': display_name
            }
    
    # Sort by baseline performance
    valid_models = [(k, v) for k, v in baseline_results.items() if 'error' not in v]
    valid_models.sort(key=lambda x: x[1]['score'], reverse=True)
    
    print(f"\n🏆 BASELINE RANKING (Code Documentation):")
    print("=" * 40)
    for i, (model_name, data) in enumerate(valid_models):
        print(f"   {i+1}. {data['display_name']}: {data['score']:.3f}")
    
    if not valid_models:
        print("❌ No models succeeded in baseline testing")
        return None
    
    # Train the top 2 models
    top_models = valid_models[:2]
    training_results = {}
    
    print(f"\n🚀 Step 2: Training top {len(top_models)} models...")
    print("-" * 40)
    
    for model_name, baseline_data in top_models:
        print(f"\n🏋️ Training {baseline_data['display_name']}...")
        
        output_dir = f"./code_docs_{model_name.replace('/', '_').replace('-', '_')}_trained"
        
        try:
            # Train the model
            result = train_model_real(
                model_name=model_name,
                template_path=template_path,
                output_dir=output_dir,
                num_epochs=3,
                learning_rate=5e-5,
                training_data_path="datasets/code_docs_training/train.jsonl"
            )
            
            if result['status'] == 'success':
                # Test trained model
                print(f"   🧪 Testing trained model...")
                trained_results, trained_score = test_model(
                    output_dir, 
                    f"TRAINED-CODE-DOCS-{baseline_data['display_name']}", 
                    template_path
                )
                
                improvement = trained_score - baseline_data['score']
                improvement_pct = (improvement / baseline_data['score'] * 100) if baseline_data['score'] > 0 else 0
                
                training_results[model_name] = {
                    'baseline_score': baseline_data['score'],
                    'trained_score': trained_score,
                    'improvement': improvement,
                    'improvement_pct': improvement_pct,
                    'status': 'success',
                    'model_path': output_dir,
                    'display_name': baseline_data['display_name']
                }
                
                print(f"   📊 Results: {baseline_data['score']:.3f} → {trained_score:.3f} ({improvement_pct:+.1f}%)")
                
            else:
                print(f"   ❌ Training failed: {result}")
                training_results[model_name] = {
                    'status': 'failed',
                    'error': result,
                    'display_name': baseline_data['display_name']
                }
                
        except Exception as e:
            print(f"   ❌ Exception during training: {e}")
            training_results[model_name] = {
                'status': 'failed',
                'error': str(e),
                'display_name': baseline_data['display_name']
            }
    
    # Final results
    print(f"\n📊 EXPERIMENT 2 RESULTS: Code Documentation Skill")
    print("=" * 60)
    
    successful_training = [(k, v) for k, v in training_results.items() if v.get('status') == 'success']
    if successful_training:
        successful_training.sort(key=lambda x: x[1]['improvement_pct'], reverse=True)
        
        print("🏆 TRAINING RESULTS:")
        for i, (model_name, data) in enumerate(successful_training):
            print(f"   {i+1}. {data['display_name']}")
            print(f"      📈 {data['baseline_score']:.3f} → {data['trained_score']:.3f} ({data['improvement_pct']:+.1f}%)")
            print(f"      📁 Saved to: {data['model_path']}")
        
        best_model = successful_training[0]
        print(f"\n🥇 BEST PERFORMING MODEL:")
        print(f"   Model: {best_model[1]['display_name']}")
        print(f"   Improvement: {best_model[1]['improvement_pct']:+.1f}%")
        print(f"   Path: {best_model[1]['model_path']}")
        
        # Save detailed results
        results_file = f"experiment_2_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'experiment': 'Code Documentation Skill Transfer',
                'timestamp': datetime.now().isoformat(),
                'template_used': template_path,
                'baseline_results': baseline_results,
                'training_results': training_results,
                'best_model': dict(best_model[1], model_name=best_model[0])
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        return best_model
        
    else:
        print("❌ No models successfully completed training")
        return None

def create_code_documentation_samples():
    """Generate training data for code documentation"""
    
    print("\n🔧 Creating code documentation training samples...")
    
    training_samples = [
        {
            "text": "Here's how to create a Python function with proper documentation:\n\n```python\ndef calculate_area(radius):\n    \"\"\"\n    Calculate the area of a circle given its radius.\n    \n    Args:\n        radius (float): The radius of the circle\n        \n    Returns:\n        float: The area of the circle\n        \n    Example:\n        >>> calculate_area(5)\n        78.54\n    \"\"\"\n    import math\n    return math.pi * radius ** 2\n```\n\nThis function includes a docstring explaining the purpose, parameters, return value, and provides a usage example."
        },
        {
            "text": "Best practices for API endpoint documentation:\n\n```python\n@app.route('/users/<int:user_id>', methods=['GET'])\ndef get_user(user_id):\n    \"\"\"\n    Retrieve user information by ID.\n    \n    Args:\n        user_id (int): The unique identifier for the user\n        \n    Returns:\n        JSON response with user data:\n        {\n            \"id\": 123,\n            \"name\": \"John Doe\",\n            \"email\": \"john@example.com\"\n        }\n        \n    Status Codes:\n        200: Success\n        404: User not found\n        400: Invalid user ID\n    \"\"\"\n    # Implementation here\n```\n\nAlways document parameters, return values, and possible status codes."
        },
        {
            "text": "How to write clear code comments:\n\n```python\n# Calculate compound interest using the formula A = P(1 + r/n)^(nt)\ndef compound_interest(principal, rate, times_compounded, years):\n    # Convert percentage to decimal (e.g., 5% = 0.05)\n    rate_decimal = rate / 100\n    \n    # Apply the compound interest formula\n    amount = principal * (1 + rate_decimal / times_compounded) ** (times_compounded * years)\n    \n    # Return the final amount minus the principal to get interest earned\n    return amount - principal\n```\n\nGood comments explain the 'why' behind the code, not just the 'what'."
        }
    ]
    
    # Save to training data file
    import os
    os.makedirs('datasets/code_docs_training', exist_ok=True)
    
    with open('datasets/code_docs_training/train.jsonl', 'w') as f:
        for sample in training_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"✅ Created {len(training_samples)} code documentation training samples")
    print("📁 Saved to: datasets/code_docs_training/train.jsonl")

if __name__ == "__main__":
    # Create training data first
    create_code_documentation_samples()
    
    # Run the experiment
    result = test_code_documentation_models()
    
    if result:
        print(f"\n🎉 EXPERIMENT 2 COMPLETE!")
        print(f"Best model: {result[1]['display_name']} ({result[1]['improvement_pct']:+.1f}%)")
    else:
        print(f"\n😞 EXPERIMENT 2 FAILED - No successful model training")