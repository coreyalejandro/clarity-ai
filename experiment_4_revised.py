"""
Experiment 4 (Revised): Multi-Skill Models Using Teaching Principles
Based on special education rubric approach for complex skill development
"""
import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model
from fix_trainer_simple import train_model_real
from clarity.scorer import score, Template

def test_teaching_multi_skill():
    """Test multi-skill training using teaching-based template and structured data"""
    
    print("🎓 EXPERIMENT 4 (REVISED): Teaching-Based Multi-Skill Training")
    print("=" * 70)
    print("Using: Special education principles + explicit rubric structure")
    
    # Use successful model and teaching-based resources
    model_name = "microsoft/DialoGPT-small"
    teaching_template = "templates/teaching_multi_skill.yaml"
    teaching_data = "datasets/teaching_multi_skill/train.jsonl"
    
    print(f"\n🔬 Training with Teaching Approach")
    print("=" * 40)
    print("✅ Template: Explicit rubric with step-by-step structure")
    print("✅ Data: Teaching-structured samples with examples + warnings")
    print("✅ Approach: Autism education principles")
    
    try:
        # Test baseline performance across skill areas
        print(f"\n📊 Testing baseline performance...")
        
        skill_templates = {
            "general": "templates/demo.yaml",
            "medical": "templates/medical_writing_fixed.yaml",
            "technical": "templates/technical_writing_fixed.yaml", 
            "teaching_multi": "templates/teaching_multi_skill.yaml"
        }
        
        baseline_scores = {}
        
        for skill_name, skill_template in skill_templates.items():
            baseline_results, baseline_score = test_model(
                model_name,
                f"TEACHING-BASELINE-{skill_name.upper()}",
                skill_template
            )
            baseline_scores[skill_name] = baseline_score
            print(f"   📈 Baseline {skill_name}: {baseline_score:.3f}")
        
        # Train with teaching-structured approach
        output_dir = "./teaching_multi_skill_model"
        
        print(f"\n🎓 Training with Teaching Principles...")
        print("   • Explicit step-by-step structure")
        print("   • Clear examples and warnings")
        print("   • Success criteria definition")
        
        training_result = train_model_real(
            model_name=model_name,
            template_path=teaching_template,
            training_data_path=teaching_data,
            output_dir=output_dir,
            num_epochs=4,  # Balanced training
            learning_rate=5e-5  # Standard rate for structured learning
        )
        
        if training_result['status'] == 'success':
            print("✅ Teaching-based training completed!")
            
            # Test trained model across all skill areas
            print(f"\n🧪 Testing teaching-trained model...")
            
            trained_scores = {}
            improvements = {}
            
            for skill_name, skill_template in skill_templates.items():
                trained_results, trained_score = test_model(
                    output_dir,
                    f"TEACHING-TRAINED-{skill_name.upper()}",
                    skill_template
                )
                
                trained_scores[skill_name] = trained_score
                improvement = trained_score - baseline_scores[skill_name]
                improvement_pct = (improvement / baseline_scores[skill_name] * 100) if baseline_scores[skill_name] > 0 else 0
                improvements[skill_name] = improvement_pct
                
                status = "🚀" if improvement_pct > 5 else "✅" if improvement_pct > 0 else "⚠️" if improvement_pct > -10 else "❌"
                print(f"   {status} {skill_name.title()}: {baseline_scores[skill_name]:.3f} → {trained_score:.3f} ({improvement_pct:+.1f}%)")
            
            # Analyze teaching effectiveness
            print(f"\n📊 TEACHING-BASED MULTI-SKILL ANALYSIS")
            print("=" * 50)
            
            # Overall performance
            avg_baseline = sum(baseline_scores.values()) / len(baseline_scores)
            avg_trained = sum(trained_scores.values()) / len(trained_scores)
            overall_improvement = (avg_trained - avg_baseline) / avg_baseline * 100 if avg_baseline > 0 else 0
            
            print(f"🎯 Overall Teaching Impact:")
            print(f"   Average Baseline: {avg_baseline:.3f}")
            print(f"   Average Teaching-Trained: {avg_trained:.3f}")  
            print(f"   Teaching Improvement: {overall_improvement:+.1f}%")
            
            # Multi-skill specific analysis
            if 'teaching_multi' in trained_scores:
                multi_improvement = improvements['teaching_multi']
                print(f"\n🎓 Multi-Skill Template Performance:")
                print(f"   Baseline: {baseline_scores['teaching_multi']:.3f}")
                print(f"   Teaching-Trained: {trained_scores['teaching_multi']:.3f}")
                print(f"   Multi-Skill Gain: {multi_improvement:+.1f}%")
            
            # Skill balance analysis
            print(f"\n⚖️ Skill Balance Analysis:")
            skill_values = list(trained_scores.values())
            skill_range = max(skill_values) - min(skill_values)
            
            if skill_range < 0.1:
                balance_status = "✅ EXCELLENT balance"
            elif skill_range < 0.2:
                balance_status = "👍 GOOD balance" 
            else:
                balance_status = "⚠️ UNBALANCED skills"
                
            print(f"   Skill Range: {skill_range:.3f} ({balance_status})")
            
            # Success criteria (teaching approach)
            print(f"\n🏆 TEACHING SUCCESS CRITERIA:")
            
            improved_count = len([imp for imp in improvements.values() if imp > 0])
            total_skills = len(improvements)
            
            success_rate = improved_count / total_skills * 100
            
            if success_rate >= 75:
                teaching_success = "🎉 TEACHING SUCCESS! Multi-skill learning achieved"
            elif success_rate >= 50:
                teaching_success = "👍 TEACHING PROGRESS! Partial multi-skill success"
            else:
                teaching_success = "🔧 NEEDS REFINEMENT: Teaching approach requires adjustment"
                
            print(f"   Skills Improved: {improved_count}/{total_skills} ({success_rate:.0f}%)")
            print(f"   Assessment: {teaching_success}")
            
            # Compare with previous multi-skill attempt
            if overall_improvement > -2.2:  # Previous attempt was -2.2%
                print(f"\n📈 TEACHING ADVANTAGE:")
                advantage = overall_improvement - (-2.2)
                print(f"   Teaching approach: {overall_improvement:+.1f}%")
                print(f"   Previous approach: -2.2%")
                print(f"   Teaching advantage: +{advantage:.1f} percentage points")
                print(f"   ✅ Teaching principles prove superior!")
            
            # Save results
            results = {
                'approach': 'teaching_based_multi_skill',
                'model_name': model_name,
                'template_used': teaching_template,
                'training_data': teaching_data,
                'baseline_scores': baseline_scores,
                'trained_scores': trained_scores,
                'improvements': improvements,
                'overall_improvement': overall_improvement,
                'success_rate': success_rate,
                'skill_balance_range': skill_range,
                'output_path': output_dir
            }
            
            results_file = f"experiment_4_teaching_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump({
                    'experiment': 'Multi-Skill Training (Teaching-Based)',
                    'timestamp': datetime.now().isoformat(),
                    'teaching_principles': [
                        'Explicit step-by-step structure',
                        'Concrete examples with context', 
                        'Clear actionable instructions',
                        'Safety warnings and cautions',
                        'Success criteria definition',
                        'Multi-domain vocabulary integration'
                    ],
                    'results': results
                }, f, indent=2)
            
            print(f"\n📄 Teaching results saved to: {results_file}")
            
            return results
            
        else:
            print(f"❌ Teaching-based training failed: {training_result}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during teaching experiment: {e}")
        return None

if __name__ == "__main__":
    print("🎓 EXPERIMENT 4 (REVISED): Teaching-Based Multi-Skill Training")
    print("Applying special education principles to model repurposing")
    print("=" * 70)
    
    results = test_teaching_multi_skill()
    
    if results:
        print(f"\n🎉 TEACHING EXPERIMENT COMPLETE!")
        print(f"Teaching approach: {results['overall_improvement']:+.1f}% overall improvement")
        print(f"Success rate: {results['success_rate']:.0f}% of skills improved")
        print(f"📁 Teaching model: {results['output_path']}")
        
        if results['overall_improvement'] > 0:
            print("🏆 TEACHING PRINCIPLES VALIDATED!")
            print("Special education rubric approach succeeds for AI training")
        else:
            print("🔧 Teaching approach shows promise - further refinement needed")
            
    else:
        print(f"\n😞 TEACHING EXPERIMENT FAILED")
        print("Need to investigate teaching approach implementation")