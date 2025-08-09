"""
Test multiple models to find the best one for ClarityAI
"""
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model

def test_multiple_models():
    """Test different base models"""
    
    models_to_test = [
        "microsoft/DialoGPT-small",  # Current
        "gpt2",
        "gpt2-medium", 
        "distilgpt2"
    ]
    
    results = []
    
    print("🧪 TESTING MULTIPLE BASE MODELS")
    print("="*50)
    
    for model_name in models_to_test:
        print(f"\n🔬 Testing {model_name}...")
        try:
            _, avg_score = test_model(model_name, f"BASELINE-{model_name}")
            results.append({
                'model': model_name,
                'score': avg_score
            })
            print(f"   ✅ Average Score: {avg_score:.3f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                'model': model_name, 
                'score': 0.0,
                'error': str(e)
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n🏆 BASELINE MODEL RANKING:")
    print("="*30)
    for i, result in enumerate(results):
        if 'error' not in result:
            print(f"   {i+1}. {result['model']}: {result['score']:.3f}")
        else:
            print(f"   {i+1}. {result['model']}: ERROR")
    
    return results

if __name__ == "__main__":
    test_multiple_models()
