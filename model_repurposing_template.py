"""
Template for Repurposing Models with Custom Scoring
Based on ClarityAI's successful DialoGPT transformation
"""
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')

def repurpose_model(
    base_model="gpt2",
    target_skill="helpful_documentation", 
    training_data_path="datasets/custom_training/train.jsonl",
    scoring_template="templates/custom.yaml",
    output_dir="repurposed_model"
):
    """
    Repurpose any model for a new skill using custom scoring
    
    Args:
        base_model: HuggingFace model to start with
        target_skill: Name of skill you're adding
        training_data_path: Path to training data
        scoring_template: ClarityAI template for target skill
        output_dir: Where to save the repurposed model
    """
    
    print(f"🔄 REPURPOSING {base_model} for {target_skill}")
    print("="*60)
    
    # Step 1: Test baseline performance
    print("🧪 Step 1: Testing baseline performance...")
    from compare_models import test_model
    baseline_results, baseline_score = test_model(base_model, f"BASELINE-{target_skill}")
    print(f"   Baseline score: {baseline_score:.3f}")
    
    # Step 2: Train the model
    print("🚀 Step 2: Training model...")
    from fix_trainer_simple import train_model_real
    
    result = train_model_real(
        model_name=base_model,
        template_path=scoring_template,
        output_dir=output_dir,
        num_epochs=5
    )
    
    if result['status'] != 'success':
        print(f"❌ Training failed: {result}")
        return None
    
    # Step 3: Test trained performance
    print("🧪 Step 3: Testing trained performance...")
    trained_results, trained_score = test_model(output_dir, f"TRAINED-{target_skill}")
    
    # Step 4: Calculate improvement
    improvement = trained_score - baseline_score
    improvement_pct = (improvement / baseline_score * 100) if baseline_score > 0 else 0
    
    print(f"\n📊 REPURPOSING RESULTS:")
    print(f"   Original model: {base_model}")
    print(f"   Target skill: {target_skill}")
    print(f"   Baseline score: {baseline_score:.3f}")
    print(f"   Trained score: {trained_score:.3f}")
    print(f"   Improvement: +{improvement:.3f} ({improvement_pct:+.1f}%)")
    
    if improvement > 0:
        print(f"✅ SUCCESS! Model repurposed successfully!")
        print(f"📁 Repurposed model saved to: {output_dir}")
        return {
            'success': True,
            'baseline_score': baseline_score,
            'trained_score': trained_score,
            'improvement': improvement,
            'model_path': output_dir
        }
    else:
        print(f"❌ FAILED! Model did not improve.")
        return {'success': False}

# Example usage:
if __name__ == "__main__":
    # Repurpose GPT-2 for helpful documentation
    result = repurpose_model(
        base_model="gpt2",
        target_skill="helpful_documentation",
        training_data_path="datasets/clarity_training/train.jsonl",
        scoring_template="templates/demo.yaml",
        output_dir="gpt2_repurposed"
    )
