"""
Fix the domain templates by converting them to proper ClarityAI rule format
"""
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def create_medical_template():
    """Create a working medical writing template with actual rules"""
    
    template = Template("medical_writing")
    
    # Medical accuracy indicators
    medical_phrases = [
        "consult your doctor", "healthcare provider", "medical professional",
        "evidence-based", "clinical studies", "FDA approved", "prescription",
        "symptoms include", "risk factors", "treatment options", "prevention",
        "safety", "side effects", "dosage", "medical history", "diagnosis"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=3.0,
        phrases=medical_phrases,
        min_matches=2
    )
    
    # Patient-friendly clarity
    clarity_phrases = [
        "clear", "understand", "simple", "easy", "step-by-step",
        "practical", "helpful", "guide", "information", "explain"
    ]
    
    template.add_rule(
        "contains_phrase", 
        weight=2.5,
        phrases=clarity_phrases,
        min_matches=1
    )
    
    # Safety emphasis
    safety_phrases = [
        "always consult", "seek immediate", "emergency", "warning",
        "do not", "avoid", "safely", "proper", "when to see"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.0,
        phrases=safety_phrases,
        min_matches=1
    )
    
    # Appropriate length
    template.add_rule(
        "word_count",
        weight=1.0,
        min_words=20,
        max_words=200
    )
    
    # Positive tone
    template.add_rule(
        "sentiment_positive",
        weight=1.5,
        min_score=0.1
    )
    
    return template

def create_technical_template():
    """Create a working technical writing template with actual rules"""
    
    template = Template("technical_writing")
    
    # Technical accuracy indicators
    technical_phrases = [
        "configuration", "implementation", "optimization", "performance",
        "system", "database", "network", "security", "deployment",
        "monitoring", "troubleshooting", "best practices", "procedures",
        "requirements", "specifications", "testing", "maintenance"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.5,
        phrases=technical_phrases,
        min_matches=2
    )
    
    # Practical implementation focus
    practical_phrases = [
        "step-by-step", "how to", "implementation", "configure", 
        "install", "setup", "execute", "run", "commands", "scripts",
        "examples", "code", "tutorial", "guide", "instructions"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.5,
        phrases=practical_phrases,
        min_matches=1
    )
    
    # Professional terminology
    professional_phrases = [
        "analysis", "assessment", "methodology", "framework",
        "architecture", "design", "standards", "protocols",
        "metrics", "benchmarks", "documentation", "specifications"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.0,
        phrases=professional_phrases,
        min_matches=1
    )
    
    # Completeness (good length)
    template.add_rule(
        "word_count",
        weight=1.5,
        min_words=30,
        max_words=300
    )
    
    # Clear structure (avoid run-on sentences)
    template.add_rule(
        "regex_match",
        weight=1.0,
        pattern=r'\. [A-Z]',  # Sentences that end and start properly
        min_matches=2
    )
    
    return template

def save_templates():
    """Save the working templates"""
    
    print("🛠️ FIXING DOMAIN TEMPLATES")
    print("=" * 40)
    
    # Create and save medical template
    medical_template = create_medical_template()
    medical_template.to_yaml("templates/medical_writing_fixed.yaml")
    print(f"✅ Created medical template with {len(medical_template.rules)} rules")
    
    # Create and save technical template  
    technical_template = create_technical_template()
    technical_template.to_yaml("templates/technical_writing_fixed.yaml")
    print(f"✅ Created technical template with {len(technical_template.rules)} rules")
    
    return medical_template, technical_template

def test_fixed_templates():
    """Test the fixed templates"""
    
    print(f"\n🧪 TESTING FIXED TEMPLATES")
    print("-" * 30)
    
    # Test content
    test_samples = {
        "good_medical": "Understanding diabetes requires consulting your healthcare provider for proper treatment options. This evidence-based guide provides clear, step-by-step information about managing blood sugar levels safely. Always seek medical advice before changing your prescription medications or dosage.",
        
        "good_technical": "Database optimization requires systematic performance analysis and implementation of best practices. Configure monitoring tools to assess query execution plans and identify bottlenecks. Follow these step-by-step procedures to optimize indexes and improve system performance through proper maintenance protocols.",
        
        "poor_content": "This is bad."
    }
    
    templates = {
        "medical": Template.from_yaml("templates/medical_writing_fixed.yaml"),
        "technical": Template.from_yaml("templates/technical_writing_fixed.yaml")
    }
    
    from clarity.scorer import score
    
    for template_name, template in templates.items():
        print(f"\n📋 {template_name.title()} Template ({len(template.rules)} rules):")
        
        for sample_name, content in test_samples.items():
            sample_score = score(content, template)
            print(f"   {sample_name}: {sample_score:.3f}")

if __name__ == "__main__":
    medical_template, technical_template = save_templates()
    test_fixed_templates()
    
    print(f"\n🎯 TEMPLATES FIXED!")
    print("Now re-run Experiment 3 with:")
    print("- templates/medical_writing_fixed.yaml")
    print("- templates/technical_writing_fixed.yaml")