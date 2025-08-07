"""
Simple Training Workflow for ClarityAI
Step-by-step training, monitoring, and evaluation
"""
import os
import sys
import json
from datetime import datetime

# Add clarity-ai to path
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')

def step1_check_data():
    """Step 1: Check training data quality"""
    print("🔍 STEP 1: Checking Training Data")
    print("="*50)
    
    # Check if data files exist
    train_file = "datasets/clarity_training/train.jsonl"
    val_file = "datasets/clarity_training/val.jsonl"
    
    if not os.path.exists(train_file):
        print("❌ Training data not found!")
        print("   Run: python create_training_data.py")
        return False
    
    if not os.path.exists(val_file):
        print("❌ Validation data not found!")
        print("   Run: python create_training_data.py")
        return False
    
    # Count samples
    with open(train_file, 'r') as f:
        train_count = len(f.readlines())
    
    with open(val_file, 'r') as f:
        val_count = len(f.readlines())
    
    print(f"✅ Training samples: {train_count}")
    print(f"✅ Validation samples: {val_count}")
    
    if train_count < 50:
        print("⚠️  Warning: Low training sample count. Consider adding more data.")
    
    print("\n📊 Sample quality test:")
    try:
        from clarity.scorer import Template
        template = Template.from_yaml("templates/demo.yaml")
        
        # Test first 3 samples
        with open(train_file, 'r') as f:
            samples = [json.loads(line)['text'] for line in f.readlines()[:3]]
        
        scores = []
        for i, sample in enumerate(samples):
            score = template.evaluate(sample)
            scores.append(score)
            print(f"   Sample {i+1}: {score:.3f}")
        
        avg_score = sum(scores) / len(scores)
        print(f"   Average: {avg_score:.3f}")
        
        if avg_score > 0.5:
            print("✅ Good quality training data!")
        else:
            print("⚠️  Consider improving sample quality")
            
    except Exception as e:
        print(f"❌ Error testing samples: {e}")
        return False
    
    print("\n✅ Step 1 Complete - Data looks good!")
    return True

def step2_baseline_test():
    """Step 2: Test baseline model performance"""
    print("\n🧪 STEP 2: Testing Baseline Model")
    print("="*50)
    
    try:
        from compare_models import test_model
        
        print("Testing original model...")
        results, avg_score = test_model("microsoft/DialoGPT-small", "BASELINE")
        
        print(f"✅ Baseline average score: {avg_score:.3f}")
        
        # Save baseline results
        baseline_results = {
            'timestamp': datetime.now().isoformat(),
            'model': 'microsoft/DialoGPT-small',
            'average_score': avg_score,
            'results': results
        }
        
        with open('baseline_results.json', 'w') as f:
            json.dump(baseline_results, f, indent=2)
        
        print("✅ Step 2 Complete - Baseline recorded!")
        return avg_score
        
    except Exception as e:
        print(f"❌ Error testing baseline: {e}")
        return None

def step3_train_model():
    """Step 3: Train the model"""
    print("\n🚀 STEP 3: Training Model")
    print("="*50)
    
    try:
        from fix_trainer_simple import train_model_real
        
        print("Starting training...")
        result = train_model_real(
            model_name="microsoft/DialoGPT-small",
            template_path="templates/demo.yaml",
            output_dir="./trained_model_v2",
            num_epochs=5,  # More epochs with better data
            learning_rate=1e-4  # Slightly higher learning rate
        )
        
        if result['status'] == 'success':
            print(f"✅ Training completed!")
            print(f"   Model saved to: {result['model_path']}")
            return result['model_path']
        else:
            print(f"❌ Training failed: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return None

def step4_evaluate_trained_model(model_path, baseline_score):
    """Step 4: Evaluate the trained model"""
    print(f"\n📈 STEP 4: Evaluating Trained Model")
    print("="*50)
    
    try:
        from compare_models import test_model
        
        print("Testing trained model...")
        results, avg_score = test_model(model_path, "TRAINED")
        
        print(f"✅ Trained model average score: {avg_score:.3f}")
        print(f"📊 Baseline score: {baseline_score:.3f}")
        
        improvement = avg_score - baseline_score
        improvement_percent = (improvement / baseline_score * 100) if baseline_score > 0 else 0
        
        if improvement > 0:
            print(f"🎉 IMPROVEMENT: +{improvement:.3f} ({improvement_percent:+.1f}%)")
            print("✅ Model got better!")
        elif improvement < 0:
            print(f"😞 DECLINE: {improvement:.3f} ({improvement_percent:+.1f}%)")
            print("❌ Model got worse - may need more training")
        else:
            print("➖ NO CHANGE")
        
        # Save results
        evaluation_results = {
            'timestamp': datetime.now().isoformat(),
            'model_path': model_path,
            'trained_score': avg_score,
            'baseline_score': baseline_score,
            'improvement': improvement,
            'improvement_percent': improvement_percent,
            'results': results
        }
        
        with open('evaluation_results.json', 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        print("✅ Step 4 Complete - Evaluation saved!")
        return avg_score > baseline_score
        
    except Exception as e:
        print(f"❌ Error evaluating model: {e}")
        return False

def step5_save_best_model(model_path, improved):
    """Step 5: Save the best model"""
    print(f"\n💾 STEP 5: Managing Models")
    print("="*50)
    
    if improved:
        print("🎉 Trained model is better! Keeping it as the best model.")
        
        # Could copy to a 'best_model' directory
        import shutil
        if os.path.exists('best_model'):
            shutil.rmtree('best_model')
        shutil.copytree(model_path, 'best_model')
        
        print(f"✅ Best model saved to: best_model/")
    else:
        print("😞 Trained model didn't improve. Keeping baseline.")
        print("💡 Suggestions:")
        print("   - Add more/better training data")
        print("   - Try different hyperparameters")
        print("   - Use a different base model")
    
    print("✅ Step 5 Complete!")

def main():
    """Run complete training workflow"""
    print("🚀 CLARITYAI TRAINING WORKFLOW")
    print("="*60)
    print("This will guide you through:")
    print("1. Check data quality")
    print("2. Test baseline model")  
    print("3. Train new model")
    print("4. Evaluate results")
    print("5. Save best model")
    print("="*60)
    
    # Run workflow
    if not step1_check_data():
        print("\n❌ Workflow stopped - fix data issues first")
        return
    
    baseline_score = step2_baseline_test()
    if baseline_score is None:
        print("\n❌ Workflow stopped - baseline test failed")
        return
    
    model_path = step3_train_model()
    if model_path is None:
        print("\n❌ Workflow stopped - training failed")
        return
    
    improved = step4_evaluate_trained_model(model_path, baseline_score)
    
    step5_save_best_model(model_path, improved)
    
    print("\n🎉 WORKFLOW COMPLETE!")
    print("="*60)
    print("📁 Check these files for results:")
    print("   - baseline_results.json")
    print("   - evaluation_results.json")
    print("   - best_model/ (if improved)")
    print("\n💻 Monitor training with:")
    print("   streamlit run training_monitor.py")

if __name__ == "__main__":
    main()