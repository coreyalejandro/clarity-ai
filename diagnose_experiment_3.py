"""
Diagnose why Experiment 3 failed - all models scored 0.000
"""
import sys
import json

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import score, Template

def diagnose_scoring_issue():
    """Check if the scoring templates are working correctly"""
    
    print("🔍 DIAGNOSING EXPERIMENT 3 FAILURE")
    print("=" * 50)
    
    # Test the templates directly
    templates_to_test = [
        "templates/demo.yaml",
        "templates/medical_writing.yaml", 
        "templates/technical_writing.yaml"
    ]
    
    # Test content samples
    test_samples = [
        {
            "name": "Good Medical Content",
            "text": "Understanding diabetes requires clear, practical information. Diabetes is a condition where blood sugar levels become too high. Always consult your healthcare provider before making changes to your diabetes management plan."
        },
        {
            "name": "Good Technical Content", 
            "text": "Database optimization requires systematic performance analysis. Start by identifying slow queries using query execution plans. Regular maintenance tasks include updating statistics and rebuilding fragmented indexes."
        },
        {
            "name": "Poor Content",
            "text": "This is bad content that doesn't help anyone."
        },
        {
            "name": "Empty Content",
            "text": ""
        },
        {
            "name": "Single Character",
            "text": "P"
        }
    ]
    
    print("\n📋 Testing Template Functionality:")
    
    for template_path in templates_to_test:
        print(f"\n🔧 Template: {template_path}")
        
        try:
            template = Template.from_yaml(template_path)
            print(f"   ✅ Template loaded successfully")
            print(f"   📊 Template name: {template.name}")
            print(f"   📝 Rules count: {len(template.rules)}")
            
            # Test each sample
            for sample in test_samples:
                try:
                    sample_score = score(sample["text"], template)
                    print(f"   📝 {sample['name']}: {sample_score:.3f}")
                except Exception as e:
                    print(f"   ❌ {sample['name']}: Error - {e}")
                    
        except Exception as e:
            print(f"   ❌ Failed to load template: {e}")
    
    print(f"\n🔬 Testing Model Output Examples:")
    
    # Test actual model outputs from the experiment
    model_outputs = [
        "Don't forget to sign up for our free newsletter to receive the latest news and reviews on new products and services from a trusted source like Amazon",
        "How to Know when your Mac is Running With Ubuntu?",
        "",
        "P",
        "go with something you like more, but are comfortable using."
    ]
    
    demo_template = Template.from_yaml("templates/demo.yaml")
    
    for i, output in enumerate(model_outputs):
        output_score = score(output, demo_template)
        print(f"   Output {i+1}: {output_score:.3f} - '{output[:50]}...'")

def check_template_rules():
    """Check what rules are actually in the templates"""
    
    print(f"\n🔍 TEMPLATE RULES ANALYSIS:")
    
    templates = [
        "templates/demo.yaml",
        "templates/medical_writing.yaml",
        "templates/technical_writing.yaml"
    ]
    
    for template_path in templates:
        print(f"\n📋 {template_path}:")
        
        try:
            template = Template.from_yaml(template_path)
            
            print(f"   Name: {template.name}")
            print(f"   Rules: {len(template.rules)}")
            
            for i, rule in enumerate(template.rules):
                print(f"     {i+1}. Type: {rule.rule_type}, Weight: {rule.weight}")
                if hasattr(rule, 'phrases') and rule.phrases:
                    print(f"        Phrases: {rule.phrases[:3]}")  # Show first 3 phrases
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_with_known_good_content():
    """Test with content we know should score well"""
    
    print(f"\n✅ TESTING WITH KNOWN GOOD CONTENT:")
    
    # This is the content that scored 0.491 in previous experiments
    good_content = "This comprehensive resource provides step-by-step guidance with clear examples and actionable advice for success. Follow these proven methods to understand key concepts and implement effective solutions."
    
    templates = [
        "templates/demo.yaml",
        "templates/medical_writing.yaml", 
        "templates/technical_writing.yaml"
    ]
    
    for template_path in templates:
        template = Template.from_yaml(template_path)
        good_score = score(good_content, template)
        print(f"   {template_path}: {good_score:.3f}")

def create_debugging_report():
    """Create a comprehensive debugging report"""
    
    print(f"\n📊 EXPERIMENT 3 FAILURE ANALYSIS:")
    print("=" * 40)
    
    print("🔍 LIKELY CAUSES:")
    print("1. Template rules may not match domain-specific content")
    print("2. Model outputs too short/irrelevant for scoring")
    print("3. Prompt templates not optimized for specialized domains")
    print("4. Training data insufficient (only 3 samples per domain)")
    print("5. Models may need different generation parameters")
    
    print(f"\n🛠️ PROPOSED FIXES:")
    print("1. Use goal-oriented prompts from Experiment 2")
    print("2. Increase training data to 10+ samples per domain") 
    print("3. Adjust generation parameters (longer outputs, temperature)")
    print("4. Use the successful DialoGPT approach from original experiment")
    print("5. Test templates with domain-specific positive indicators")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Fix prompts to use goal-oriented format")
    print("2. Generate more domain-specific training data")  
    print("3. Use optimized generation parameters")
    print("4. Re-run with the successful model (DialoGPT) first")

if __name__ == "__main__":
    diagnose_scoring_issue()
    check_template_rules()
    test_with_known_good_content()
    create_debugging_report()