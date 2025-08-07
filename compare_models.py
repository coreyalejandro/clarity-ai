"""
Compare the original model vs trained model performance
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def test_model(model_path, model_name, template_path="templates/demo.yaml"):
    """Test a model and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING {model_name}")
    print(f"📁 Model path: {model_path}")
    print(f"📋 Template: {template_path}")
    print(f"{'='*60}")
    
    # Load model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    
    # Load ClarityAI template
    template = Template.from_yaml(template_path)
    
    # Test prompts based on template
    if "code_documentation" in template_path:
        test_prompts = [
            "Explain this Python function:",
            "Document this API endpoint:",
            "Write clear code comments for:",
            "Create documentation for:",
            "Explain how to use this code:"
        ]
    elif "api_documentation" in template_path:
        test_prompts = [
            "Document this API endpoint:",
            "Explain the request parameters:",
            "Show an example API call:",
            "Document the response format:",
            "Explain authentication for:"
        ]
    elif "tutorial" in template_path:
        test_prompts = [
            "Create a tutorial for:",
            "Write step-by-step instructions for:",
            "Explain how to learn:",
            "Create a beginner guide for:",
            "Write a practical tutorial on:"
        ]
    else:
        # Default prompts
        test_prompts = [
            "Write a helpful guide:",
            "Create useful content:",
            "Provide clear information:",
            "Make helpful documentation:",
            "Give practical advice:"
        ]
    
    results = []
    total_score = 0
    
    for i, prompt in enumerate(test_prompts):
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=40,
                temperature=0.8,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        clarity_score = template.evaluate(generated_text.strip())
        
        results.append({
            'prompt': prompt,
            'generated': generated_text.strip(),
            'score': clarity_score
        })
        
        total_score += clarity_score
        
        print(f"\n📝 Test {i+1}:")
        print(f"   Prompt: {prompt}")
        print(f"   Generated: {generated_text.strip()}")
        print(f"   ClarityAI Score: {clarity_score:.3f}")
    
    avg_score = total_score / len(test_prompts)
    print(f"\n📊 SUMMARY for {model_name}:")
    print(f"   Average ClarityAI Score: {avg_score:.3f}")
    print(f"   Total Tests: {len(test_prompts)}")
    
    return results, avg_score

def main():
    print("🔍 COMPARING ORIGINAL vs TRAINED MODEL PERFORMANCE")
    print("Using ClarityAI scoring to measure improvement")
    
    # Test original model
    original_results, original_avg = test_model("microsoft/DialoGPT-small", "ORIGINAL MODEL")
    
    # Test trained model  
    trained_results, trained_avg = test_model("./trained_model", "TRAINED MODEL")
    
    # Compare results
    print(f"\n{'='*60}")
    print(f"📈 FINAL COMPARISON")
    print(f"{'='*60}")
    print(f"Original Model Average Score: {original_avg:.3f}")
    print(f"Trained Model Average Score:  {trained_avg:.3f}")
    
    improvement = trained_avg - original_avg
    improvement_percent = (improvement / original_avg * 100) if original_avg > 0 else 0
    
    if improvement > 0:
        print(f"✅ IMPROVEMENT: +{improvement:.3f} ({improvement_percent:+.1f}%)")
        print(f"🎉 The model got BETTER!")
    elif improvement < 0:
        print(f"❌ DECLINE: {improvement:.3f} ({improvement_percent:+.1f}%)")
        print(f"😞 The model got worse")
    else:
        print(f"➖ NO CHANGE: Same performance")
    
    print(f"\n📊 DETAILED COMPARISON:")
    for i, (orig, trained) in enumerate(zip(original_results, trained_results)):
        score_change = trained['score'] - orig['score']
        print(f"\n   Test {i+1}: {orig['prompt']}")
        print(f"   Original: {orig['score']:.3f} | Trained: {trained['score']:.3f} | Change: {score_change:+.3f}")

if __name__ == "__main__":
    main()