"""
Experiment 4: Multi-Skill Models - Training models with multiple capabilities
Test if we can create a model that excels across general, technical, medical, and code domains
"""
import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model
from fix_trainer_simple import train_model_real
from clarity.scorer import score, Template

def create_multi_skill_training_data():
    """Create training data that combines multiple skills"""
    
    print("📊 Creating multi-skill training dataset...")
    
    # Multi-skill training samples (combining insights from all previous experiments)
    multi_skill_samples = [
        {
            "text": "Understanding database security requires systematic implementation with proper safety considerations. This comprehensive technical guide provides step-by-step procedures for configuring secure database connections with clear code examples and error handling. Always consult your security team before implementing authentication changes, follow industry best practices for password encryption, and ensure proper monitoring of access logs. Key implementation steps include: 1) Configure SSL connections with valid certificates, 2) Implement role-based access control with minimal privileges, 3) Enable audit logging for security events, and 4) Regular security assessments and vulnerability testing."
        },
        {
            "text": "API development for healthcare applications requires comprehensive understanding of both technical implementation and medical data safety requirements. This practical guide provides clear, step-by-step instructions for building HIPAA-compliant APIs with proper error handling and security measures. Essential considerations include: patient data encryption, secure authentication protocols, audit logging, and proper error responses that don't leak sensitive information. Always consult healthcare compliance experts and follow evidence-based security frameworks. Code examples demonstrate proper parameter validation, database connection security, and API documentation standards for medical applications."
        },
        {
            "text": "Network troubleshooting methodology combines systematic technical analysis with clear documentation procedures for professional IT environments. This comprehensive guide provides actionable steps for diagnosing connectivity issues, implementing monitoring solutions, and maintaining network security. Key procedures include: 1) Systematic analysis of network topology and configuration, 2) Performance monitoring with proper alerting, 3) Security assessment and vulnerability management, 4) Clear documentation of findings and recommendations. Always follow established protocols, consult network architecture specifications, and ensure proper change management procedures for production systems."
        },
        {
            "text": "Software deployment automation requires comprehensive understanding of system architecture, security considerations, and operational best practices. This detailed technical guide provides step-by-step implementation procedures for CI/CD pipelines with proper error handling, monitoring, and safety controls. Essential components include: automated testing frameworks, security scanning integration, deployment rollback procedures, and comprehensive logging. Always consult your DevOps team for production deployments, follow established security protocols, and ensure proper documentation of deployment procedures and troubleshooting guides."
        },
        {
            "text": "Medical device software development combines rigorous technical implementation with strict safety and regulatory compliance requirements. This comprehensive professional guide provides clear procedures for developing FDA-compliant medical software with proper validation, testing, and documentation. Critical considerations include: evidence-based design requirements, systematic testing procedures, risk assessment methodology, and regulatory submission documentation. Always consult medical device regulations, follow IEC 62304 standards for medical device software, implement proper configuration management, and ensure comprehensive traceability throughout the development lifecycle."
        }
    ]
    
    # Save multi-skill dataset
    os.makedirs('datasets/multi_skill_training', exist_ok=True)
    
    with open('datasets/multi_skill_training/train.jsonl', 'w') as f:
        for sample in multi_skill_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"✅ Created {len(multi_skill_samples)} multi-skill training samples")
    print("📋 Each sample combines: General + Technical + Code + Medical/Safety + Professional")
    
    return len(multi_skill_samples)

def test_multi_skill_model():
    """Test creating a multi-skill model"""
    
    print("🧪 EXPERIMENT 4: Multi-Skill Model Training")
    print("=" * 60)
    
    # Create training data
    sample_count = create_multi_skill_training_data()
    
    # Use our most successful model
    model_name = "microsoft/DialoGPT-small"
    template_path = "templates/multi_skill_fixed.yaml"
    training_data_path = "datasets/multi_skill_training/train.jsonl"
    
    print(f"\n🔬 Building Multi-Skill Model with {model_name}")
    print("=" * 50)
    
    try:
        # Test baseline across all skill areas
        print("📊 Testing baseline performance across skill areas...")
        
        skill_templates = {
            "general": "templates/demo.yaml",
            "medical": "templates/medical_writing_fixed.yaml", 
            "technical": "templates/technical_writing_fixed.yaml",
            "multi_skill": "templates/multi_skill_fixed.yaml"
        }
        
        baseline_scores = {}
        
        for skill_name, skill_template in skill_templates.items():
            baseline_results, baseline_score = test_model(
                model_name,
                f"BASELINE-{skill_name.upper()}",
                skill_template
            )
            baseline_scores[skill_name] = baseline_score
            print(f"   📈 Baseline {skill_name}: {baseline_score:.3f}")
        
        # Train multi-skill model
        output_dir = "./multi_skill_model"
        
        print(f"\n🚀 Training multi-skill model...")
        print(f"   Training data: {sample_count} comprehensive samples")
        print(f"   Target: Optimize for multi-skill template")
        
        training_result = train_model_real(
            model_name=model_name,
            template_path=template_path,
            training_data_path=training_data_path,
            output_dir=output_dir,
            num_epochs=5,  # More epochs for complex multi-skill learning
            learning_rate=3e-5  # Lower LR for stable multi-skill training
        )
        
        if training_result['status'] == 'success':
            print("✅ Multi-skill training completed!")
            
            # Test trained model across all skill areas
            print(f"\n🧪 Testing multi-skill model performance...")
            
            trained_scores = {}
            improvements = {}
            
            for skill_name, skill_template in skill_templates.items():
                trained_results, trained_score = test_model(
                    output_dir,
                    f"MULTI-SKILL-{skill_name.upper()}",
                    skill_template
                )
                
                trained_scores[skill_name] = trained_score
                improvement = trained_score - baseline_scores[skill_name]
                improvement_pct = (improvement / baseline_scores[skill_name] * 100) if baseline_scores[skill_name] > 0 else 0
                improvements[skill_name] = improvement_pct
                
                print(f"   📊 {skill_name.title()}: {baseline_scores[skill_name]:.3f} → {trained_score:.3f} ({improvement_pct:+.1f}%)")
            
            # Analyze multi-skill effectiveness
            print(f"\n📊 MULTI-SKILL ANALYSIS")
            print("=" * 40)
            
            # Overall performance
            avg_baseline = sum(baseline_scores.values()) / len(baseline_scores)
            avg_trained = sum(trained_scores.values()) / len(trained_scores)
            overall_improvement = (avg_trained - avg_baseline) / avg_baseline * 100 if avg_baseline > 0 else 0
            
            print(f"🎯 Overall Performance:")
            print(f"   Average Baseline: {avg_baseline:.3f}")
            print(f"   Average Multi-skill: {avg_trained:.3f}")
            print(f"   Overall Improvement: {overall_improvement:+.1f}%")
            
            # Skill-specific analysis
            print(f"\n🔍 Skill-Specific Results:")
            sorted_skills = sorted(improvements.items(), key=lambda x: x[1], reverse=True)
            
            for skill, improvement in sorted_skills:
                status = "✅ IMPROVED" if improvement > 0 else "⚠️ DECLINED" if improvement < -2 else "➡️ STABLE"
                print(f"   {status} {skill.title()}: {improvement:+.1f}%")
            
            # Check for skill transfer effects
            print(f"\n🔄 Multi-Skill Transfer Effects:")
            best_skill = max(trained_scores.items(), key=lambda x: x[1])
            worst_skill = min(trained_scores.items(), key=lambda x: x[1])
            
            print(f"   🏆 Strongest Skill: {best_skill[0].title()} ({best_skill[1]:.3f})")
            print(f"   🔧 Needs Work: {worst_skill[0].title()} ({worst_skill[1]:.3f})")
            
            skill_range = best_skill[1] - worst_skill[1]
            if skill_range < 0.1:
                print(f"   ✅ Balanced multi-skill performance (range: {skill_range:.3f})")
            else:
                print(f"   ⚠️ Unbalanced skills (range: {skill_range:.3f})")
            
            # Create summary results
            results = {
                'model_name': model_name,
                'training_samples': sample_count,
                'output_path': output_dir,
                'baseline_scores': baseline_scores,
                'trained_scores': trained_scores,
                'improvements': improvements,
                'overall_improvement': overall_improvement,
                'best_skill': best_skill,
                'worst_skill': worst_skill,
                'skill_balance_range': skill_range
            }
            
            # Save results
            results_file = f"experiment_4_multi_skill_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump({
                    'experiment': 'Multi-Skill Model Training',
                    'timestamp': datetime.now().isoformat(),
                    'results': results
                }, f, indent=2)
            
            print(f"\n📄 Results saved to: {results_file}")
            
            return results
            
        else:
            print(f"❌ Multi-skill training failed: {training_result}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    print("🚀 EXPERIMENT 4: Multi-Skill Models")
    print("Testing model capability across multiple domains simultaneously")
    print("=" * 70)
    
    results = test_multi_skill_model()
    
    if results:
        print(f"\n🎉 EXPERIMENT 4 COMPLETE!")
        print(f"Multi-skill model created with {results['overall_improvement']:+.1f}% overall improvement")
        print(f"📁 Model saved to: {results['output_path']}")
        
        # Check if truly multi-skilled
        improved_skills = [skill for skill, imp in results['improvements'].items() if imp > 0]
        print(f"✅ Improved in {len(improved_skills)}/{len(results['improvements'])} skill areas")
        
        if len(improved_skills) >= 3:
            print("🏆 SUCCESS: True multi-skill capability achieved!")
        elif len(improved_skills) >= 2:
            print("👍 PARTIAL: Multi-skill capability demonstrated")
        else:
            print("🔧 NEEDS WORK: Limited multi-skill transfer")
            
    else:
        print(f"\n😞 EXPERIMENT 4 FAILED")
        print("Multi-skill training needs further investigation")