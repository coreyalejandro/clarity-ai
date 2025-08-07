"""
Experiment 3: Domain Transfer - Medical/Technical Writing
Test how general models perform when repurposed for specialized domains
"""
import sys
import json
import os
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from compare_models import test_model
from fix_trainer_simple import train_model_real
from clarity.scorer import score

def create_domain_training_data():
    """Create specialized training data for domain transfer"""
    
    print("📊 Creating domain-specific training datasets...")
    
    # Medical writing training data (using goal-oriented prompts from Experiment 2)
    medical_samples = [
        {
            "text": "Understanding diabetes requires clear, practical information. Diabetes is a condition where blood sugar levels become too high. Type 1 diabetes occurs when the body cannot produce insulin, while Type 2 diabetes happens when the body doesn't use insulin properly. Key management strategies include regular blood sugar monitoring, following a balanced diet with controlled carbohydrates, taking prescribed medications as directed, and maintaining regular physical activity. Warning signs that require immediate medical attention include extreme thirst, frequent urination, blurred vision, and unexplained weight loss. Always consult your healthcare provider before making changes to your diabetes management plan."
        },
        {
            "text": "Heart health maintenance involves practical, evidence-based approaches. Regular cardiovascular exercise for 150 minutes per week helps strengthen the heart muscle and improve circulation. A heart-healthy diet emphasizes fruits, vegetables, whole grains, and lean proteins while limiting saturated fats and sodium. Key risk factors include high blood pressure, elevated cholesterol, smoking, and family history. Monitor your blood pressure regularly and maintain levels below 120/80 mmHg when possible. Schedule annual checkups with your doctor to assess cardiovascular risk factors and discuss prevention strategies tailored to your individual health profile."
        },
        {
            "text": "Managing anxiety effectively requires understanding practical coping strategies. Anxiety disorders affect millions of people and can significantly impact daily life. Evidence-based techniques include deep breathing exercises, progressive muscle relaxation, and cognitive behavioral therapy approaches. Regular exercise, adequate sleep (7-9 hours nightly), and limiting caffeine intake can help reduce anxiety symptoms. When anxiety interferes with work, relationships, or daily activities, professional help from a mental health provider is recommended. Emergency situations requiring immediate attention include panic attacks with chest pain, thoughts of self-harm, or inability to function normally."
        }
    ]
    
    # Technical writing training data
    technical_samples = [
        {
            "text": "Database optimization requires systematic performance analysis and targeted improvements. Start by identifying slow queries using query execution plans and performance monitoring tools. Index optimization involves creating indexes on frequently queried columns while avoiding over-indexing that slows write operations. Query optimization techniques include using appropriate WHERE clauses, avoiding SELECT *, and utilizing JOIN operations efficiently. Regular maintenance tasks include updating statistics, rebuilding fragmented indexes, and archiving old data. Performance benchmarking should establish baseline metrics before implementing changes and measure improvements afterward. Always test optimization changes in a development environment before applying to production systems."
        },
        {
            "text": "Network security implementation follows layered defense principles with practical security measures. Firewall configuration should block unnecessary ports while allowing legitimate traffic through specific rules. Access control management requires implementing role-based permissions, regular password updates, and multi-factor authentication for sensitive systems. Network monitoring tools help detect unusual traffic patterns, failed login attempts, and potential security breaches. Regular security audits should assess vulnerability patches, review access logs, and test backup recovery procedures. Incident response plans must define clear steps for containment, investigation, and recovery from security events."
        },
        {
            "text": "Software deployment automation streamlines release processes while ensuring reliability and consistency. Continuous integration pipelines should include automated testing, code quality checks, and security scanning before deployment. Infrastructure as code practices enable reproducible environment configuration using version-controlled templates. Blue-green deployment strategies minimize downtime by maintaining parallel production environments during updates. Monitoring and logging systems must track application performance, error rates, and user experience metrics post-deployment. Rollback procedures should be tested regularly and executable within minutes when issues occur. Documentation should cover deployment procedures, environment configurations, and troubleshooting steps."
        }
    ]
    
    # Save datasets
    os.makedirs('datasets/medical_training', exist_ok=True)
    os.makedirs('datasets/technical_training', exist_ok=True)
    
    with open('datasets/medical_training/train.jsonl', 'w') as f:
        for sample in medical_samples:
            f.write(json.dumps(sample) + '\n')
    
    with open('datasets/technical_training/train.jsonl', 'w') as f:
        for sample in technical_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"✅ Created {len(medical_samples)} medical training samples")
    print(f"✅ Created {len(technical_samples)} technical training samples")
    
    return len(medical_samples), len(technical_samples)

def test_domain_transfer():
    """Test domain transfer across different specialized areas"""
    
    print("🧪 EXPERIMENT 3: Domain Transfer - Medical/Technical Writing")
    print("=" * 70)
    
    # Create training data
    med_samples, tech_samples = create_domain_training_data()
    
    # Define domain transfer experiments
    experiments = [
        {
            "domain": "medical",
            "template": "templates/medical_writing.yaml", 
            "training_data": "datasets/medical_training/train.jsonl",
            "test_prompts": [
                "Help users understand heart disease prevention with practical, actionable information",
                "Help users understand diabetes management with practical, actionable information",
                "Help users understand mental health resources with practical, actionable information"
            ]
        },
        {
            "domain": "technical", 
            "template": "templates/technical_writing.yaml",
            "training_data": "datasets/technical_training/train.jsonl", 
            "test_prompts": [
                "Help users understand database optimization with practical, actionable information",
                "Help users understand network security with practical, actionable information", 
                "Help users understand software deployment with practical, actionable information"
            ]
        }
    ]
    
    # Models to test for domain transfer
    models_to_test = [
        ("gpt2", "GPT-2 Base"),
        ("microsoft/DialoGPT-small", "DialoGPT-small")
    ]
    
    results = {}
    
    for experiment in experiments:
        domain = experiment["domain"]
        template_path = experiment["template"] 
        training_data_path = experiment["training_data"]
        
        print(f"\n🏥 DOMAIN: {domain.upper()}")
        print("=" * 50)
        
        domain_results = {}
        
        for model_name, display_name in models_to_test:
            print(f"\n🔬 Testing {display_name} for {domain} writing...")
            
            try:
                # Test baseline performance in this domain
                print("   📊 Testing baseline performance...")
                baseline_results, baseline_score = test_model(
                    model_name, 
                    f"BASELINE-{domain.upper()}-{display_name}",
                    template_path
                )
                print(f"   📈 Baseline {domain} score: {baseline_score:.3f}")
                
                # Train model on domain-specific data
                output_dir = f"./domain_transfer_{domain}_{model_name.replace('/', '_').replace('-', '_')}"
                
                print("   🚀 Training on domain-specific data...")
                training_result = train_model_real(
                    model_name=model_name,
                    template_path=template_path,
                    training_data_path=training_data_path,
                    output_dir=output_dir,
                    num_epochs=3,
                    learning_rate=5e-5
                )
                
                if training_result['status'] == 'success':
                    # Test trained performance
                    print("   🧪 Testing domain-specialized performance...")
                    trained_results, trained_score = test_model(
                        output_dir,
                        f"DOMAIN-TRAINED-{domain.upper()}-{display_name}",
                        template_path
                    )
                    
                    # Calculate domain transfer effectiveness
                    improvement = trained_score - baseline_score
                    improvement_pct = (improvement / baseline_score * 100) if baseline_score > 0 else 0
                    
                    domain_results[model_name] = {
                        'display_name': display_name,
                        'baseline_score': baseline_score,
                        'trained_score': trained_score,
                        'improvement': improvement,
                        'improvement_pct': improvement_pct,
                        'status': 'success',
                        'model_path': output_dir
                    }
                    
                    print(f"   📊 Domain Transfer Results:")
                    print(f"      Baseline: {baseline_score:.3f}")
                    print(f"      Specialized: {trained_score:.3f}")
                    print(f"      Transfer Gain: {improvement_pct:+.1f}%")
                    
                    # Test cross-domain performance
                    print("   🔄 Testing cross-domain performance...")
                    other_domain = "technical" if domain == "medical" else "medical"
                    other_template = f"templates/{other_domain}_writing.yaml"
                    
                    cross_results, cross_score = test_model(
                        output_dir,
                        f"CROSS-DOMAIN-{other_domain.upper()}-{display_name}",
                        other_template
                    )
                    
                    domain_results[model_name]['cross_domain_score'] = cross_score
                    print(f"      Cross-domain ({other_domain}): {cross_score:.3f}")
                    
                else:
                    print(f"   ❌ Training failed: {training_result}")
                    domain_results[model_name] = {
                        'display_name': display_name,
                        'status': 'failed',
                        'error': training_result
                    }
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                domain_results[model_name] = {
                    'display_name': display_name,
                    'status': 'failed',
                    'error': str(e)
                }
        
        results[domain] = domain_results
    
    # Analyze domain transfer effectiveness
    print(f"\n📊 DOMAIN TRANSFER ANALYSIS")
    print("=" * 50)
    
    successful_transfers = []
    
    for domain, domain_data in results.items():
        for model, data in domain_data.items():
            if data.get('status') == 'success':
                successful_transfers.append({
                    'domain': domain,
                    'model': data['display_name'],
                    'improvement': data['improvement_pct'],
                    'baseline': data['baseline_score'],
                    'specialized': data['trained_score'],
                    'cross_domain': data.get('cross_domain_score', 0.0)
                })
    
    if successful_transfers:
        # Sort by improvement
        successful_transfers.sort(key=lambda x: x['improvement'], reverse=True)
        
        print("🏆 DOMAIN TRANSFER EFFECTIVENESS:")
        for i, transfer in enumerate(successful_transfers):
            print(f"   {i+1}. {transfer['model']} → {transfer['domain'].title()} Writing")
            print(f"      Domain Gain: {transfer['improvement']:+.1f}%")
            print(f"      Scores: {transfer['baseline']:.3f} → {transfer['specialized']:.3f}")
            print(f"      Cross-domain: {transfer['cross_domain']:.3f}")
        
        best_transfer = successful_transfers[0]
        print(f"\n🥇 BEST DOMAIN TRANSFER:")
        print(f"   Model: {best_transfer['model']}")
        print(f"   Domain: {best_transfer['domain'].title()} Writing")
        print(f"   Improvement: {best_transfer['improvement']:+.1f}%")
        
        # Check for domain specialization vs generalization
        avg_cross_domain = sum(t['cross_domain'] for t in successful_transfers) / len(successful_transfers)
        avg_specialized = sum(t['specialized'] for t in successful_transfers) / len(successful_transfers)
        
        print(f"\n🔍 SPECIALIZATION ANALYSIS:")
        print(f"   Average specialized performance: {avg_specialized:.3f}")
        print(f"   Average cross-domain performance: {avg_cross_domain:.3f}")
        
        if avg_specialized > avg_cross_domain:
            specialization_gain = (avg_specialized - avg_cross_domain) / avg_cross_domain * 100
            print(f"   ✅ Models successfully specialized (+{specialization_gain:.1f}% vs cross-domain)")
        else:
            print(f"   ⚠️ Limited specialization detected")
    
    # Save detailed results
    results_file = f"domain_transfer_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'experiment': 'Domain Transfer - Medical/Technical Writing',
            'timestamp': datetime.now().isoformat(),
            'training_data_sizes': {
                'medical': med_samples,
                'technical': tech_samples
            },
            'results': results,
            'successful_transfers': successful_transfers
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    print("🚀 EXPERIMENT 3: Domain Transfer")
    print("Testing model repurposing for specialized domains")
    print("=" * 60)
    
    results = test_domain_transfer()
    
    print(f"\n🎉 EXPERIMENT 3 COMPLETE!")
    print("Domain transfer effectiveness measured across medical and technical writing")