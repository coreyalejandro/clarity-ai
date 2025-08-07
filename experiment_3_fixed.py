"""
Experiment 3 (Fixed): Domain Transfer with Working Templates and Optimized Approach
Using lessons learned from previous experiments
"""
import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model
from fix_trainer_simple import train_model_real
from clarity.scorer import score

def test_domain_transfer_fixed():
    """Test domain transfer with fixed approach"""
    
    print("🧪 EXPERIMENT 3 (FIXED): Domain Transfer")
    print("=" * 50)
    print("Using: Fixed templates + DialoGPT + Goal-oriented prompts")
    
    # Use the successful model from our previous experiments
    model_to_test = "microsoft/DialoGPT-small"
    
    # Domain experiments with fixed templates
    experiments = [
        {
            "domain": "medical",
            "template": "templates/medical_writing_fixed.yaml",
            "training_data": "datasets/medical_training/train.jsonl",
        },
        {
            "domain": "technical", 
            "template": "templates/technical_writing_fixed.yaml",
            "training_data": "datasets/technical_training/train.jsonl",
        }
    ]
    
    results = {}
    
    for experiment in experiments:
        domain = experiment["domain"]
        template_path = experiment["template"]
        training_data_path = experiment["training_data"]
        
        print(f"\n🏥 DOMAIN: {domain.upper()}")
        print("=" * 30)
        
        try:
            # Test baseline performance in this domain
            print("📊 Testing baseline performance...")
            baseline_results, baseline_score = test_model(
                model_to_test, 
                f"BASELINE-{domain.upper()}-DialoGPT",
                template_path
            )
            print(f"✅ Baseline {domain} score: {baseline_score:.3f}")
            
            # Only train if baseline is working (> 0)
            if baseline_score > 0:
                # Train model on domain-specific data
                output_dir = f"./domain_transfer_{domain}_fixed"
                
                print("🚀 Training on domain-specific data...")
                training_result = train_model_real(
                    model_name=model_to_test,
                    template_path=template_path,
                    training_data_path=training_data_path,
                    output_dir=output_dir,
                    num_epochs=3,
                    learning_rate=5e-5
                )
                
                if training_result['status'] == 'success':
                    # Test trained performance
                    print("🧪 Testing domain-specialized performance...")
                    trained_results, trained_score = test_model(
                        output_dir,
                        f"DOMAIN-TRAINED-{domain.upper()}-DialoGPT",
                        template_path
                    )
                    
                    # Calculate domain transfer effectiveness
                    improvement = trained_score - baseline_score
                    improvement_pct = (improvement / baseline_score * 100) if baseline_score > 0 else 0
                    
                    results[domain] = {
                        'baseline_score': baseline_score,
                        'trained_score': trained_score,
                        'improvement': improvement,
                        'improvement_pct': improvement_pct,
                        'status': 'success',
                        'model_path': output_dir
                    }
                    
                    print(f"📊 Domain Transfer Results:")
                    print(f"   Baseline: {baseline_score:.3f}")
                    print(f"   Specialized: {trained_score:.3f}")
                    print(f"   Transfer Gain: {improvement_pct:+.1f}%")
                    
                    # Quick cross-domain test
                    other_domain = "technical" if domain == "medical" else "medical"
                    if other_domain in ["medical", "technical"]:  # Only test valid domains
                        other_template = f"templates/{other_domain}_writing_fixed.yaml"
                        print("🔄 Testing cross-domain performance...")
                        cross_results, cross_score = test_model(
                            output_dir,
                            f"CROSS-DOMAIN-{other_domain.upper()}",
                            other_template
                        )
                        results[domain]['cross_domain_score'] = cross_score
                        print(f"   Cross-domain ({other_domain}): {cross_score:.3f}")
                    
                else:
                    results[domain] = {'status': 'training_failed', 'error': training_result}
                    
            else:
                results[domain] = {'status': 'baseline_failed', 'baseline_score': baseline_score}
                print(f"⚠️ Skipping training - baseline failed ({baseline_score:.3f})")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results[domain] = {'status': 'exception', 'error': str(e)}
    
    # Analyze results
    print(f"\n📊 EXPERIMENT 3 (FIXED) RESULTS")
    print("=" * 40)
    
    successful_results = {k: v for k, v in results.items() if v.get('status') == 'success'}
    
    if successful_results:
        print("✅ SUCCESSFUL DOMAIN TRANSFERS:")
        
        for domain, data in successful_results.items():
            print(f"\n   🏆 {domain.title()} Writing:")
            print(f"      Baseline → Specialized: {data['baseline_score']:.3f} → {data['trained_score']:.3f}")
            print(f"      Domain Transfer Gain: {data['improvement_pct']:+.1f}%")
            if 'cross_domain_score' in data:
                print(f"      Cross-domain Score: {data['cross_domain_score']:.3f}")
                specialization = data['trained_score'] - data['cross_domain_score']
                print(f"      Specialization Effect: {specialization:+.3f}")
        
        # Find best transfer
        best_domain = max(successful_results.items(), key=lambda x: x[1]['improvement_pct'])
        print(f"\n🥇 BEST DOMAIN TRANSFER:")
        print(f"   Domain: {best_domain[0].title()} Writing")
        print(f"   Improvement: {best_domain[1]['improvement_pct']:+.1f}%")
        print(f"   Model Path: {best_domain[1]['model_path']}")
        
    else:
        print("❌ No successful domain transfers")
        
        # Show what failed
        for domain, data in results.items():
            print(f"   {domain}: {data.get('status', 'unknown')}")
    
    # Save results
    results_file = f"experiment_3_fixed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'experiment': 'Domain Transfer (Fixed) - Medical/Technical Writing',
            'timestamp': datetime.now().isoformat(),
            'model_used': model_to_test,
            'templates': {
                'medical': 'templates/medical_writing_fixed.yaml',
                'technical': 'templates/technical_writing_fixed.yaml'
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    print("🚀 EXPERIMENT 3 (FIXED): Domain Transfer")
    print("Applying lessons learned from previous experiments")
    print("=" * 60)
    
    results = test_domain_transfer_fixed()
    
    print(f"\n🎉 EXPERIMENT 3 (FIXED) COMPLETE!")
    
    # Update todo status based on results
    successful_count = len([r for r in results.values() if r.get('status') == 'success'])
    
    if successful_count > 0:
        print(f"✅ {successful_count} successful domain transfers achieved!")
    else:
        print("⚠️ Domain transfer needs further investigation")