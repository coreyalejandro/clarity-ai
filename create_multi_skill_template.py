"""
Create a proper multi-skill template with ClarityAI rules
Combining insights from all previous experiments
"""
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def create_multi_skill_template():
    """Create a comprehensive multi-skill template"""
    
    template = Template("multi_skill_writing")
    
    # 1. General helpfulness (from successful demo template)
    helpful_phrases = [
        "clear", "helpful", "practical", "actionable", "step-by-step",
        "useful", "effective", "guide", "information", "advice",
        "comprehensive", "detailed", "structured", "examples"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.5,
        phrases=helpful_phrases,
        min_matches=2
    )
    
    # 2. Technical implementation focus
    technical_phrases = [
        "implementation", "configuration", "optimization", "system",
        "database", "network", "performance", "monitoring", "security",
        "deployment", "troubleshooting", "best practices", "procedures"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.5,
        phrases=technical_phrases,
        min_matches=1
    )
    
    # 3. Code/documentation quality
    code_phrases = [
        "code", "function", "API", "documentation", "example",
        "syntax", "parameter", "variable", "method", "class",
        "endpoint", "response", "request", "error handling"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.0,
        phrases=code_phrases,
        min_matches=1
    )
    
    # 4. Medical/safety awareness
    safety_phrases = [
        "consult", "professional", "healthcare", "safety", "proper",
        "warning", "risk", "prevention", "evidence-based", "medical",
        "doctor", "provider", "treatment", "diagnosis", "symptoms"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.0,
        phrases=safety_phrases,
        min_matches=1
    )
    
    # 5. Professional communication quality
    professional_phrases = [
        "methodology", "framework", "analysis", "assessment",
        "standards", "protocol", "specification", "requirements",
        "documentation", "guidelines", "recommendations", "strategy"
    ]
    
    template.add_rule(
        "contains_phrase", 
        weight=1.5,
        phrases=professional_phrases,
        min_matches=1
    )
    
    # 6. Appropriate length for comprehensive content
    template.add_rule(
        "word_count",
        weight=1.5,
        min_words=25,
        max_words=250
    )
    
    # 7. Positive sentiment (helpful tone)
    template.add_rule(
        "sentiment_positive",
        weight=1.0,
        min_score=0.1
    )
    
    return template

def test_multi_skill_template():
    """Test the multi-skill template with various content types"""
    
    template = create_multi_skill_template()
    template.to_yaml("templates/multi_skill_fixed.yaml")
    
    print("🔧 Created Multi-Skill Template")
    print(f"   Rules: {len(template.rules)}")
    
    # Test with different skill combinations
    test_samples = {
        "general_helpful": "This comprehensive guide provides clear, step-by-step instructions with practical examples and actionable advice for success.",
        
        "code_focused": "This API documentation includes clear examples, proper error handling, and detailed parameter specifications. Configure the endpoint with proper authentication and follow security best practices.",
        
        "medical_aware": "Understanding diabetes requires consulting your healthcare provider for proper treatment recommendations. This evidence-based guide provides clear information about risk factors and prevention methods safely.",
        
        "technical_implementation": "Database optimization requires systematic performance analysis and implementation of monitoring procedures. Configure indexes properly and follow best practices for security and troubleshooting.",
        
        "multi_skill_combo": "This comprehensive technical guide provides step-by-step implementation procedures with clear code examples and proper safety considerations. Consult documentation for API configuration, follow security best practices, and ensure proper error handling throughout the system.",
        
        "poor_content": "Bad info here."
    }
    
    print(f"\n🧪 Testing Multi-Skill Template:")
    
    from clarity.scorer import score
    
    for name, content in test_samples.items():
        sample_score = score(content, template)
        print(f"   {name}: {sample_score:.3f}")
        if name == "multi_skill_combo":
            print(f"      (Expected highest - combines all skills)")
    
    return template

if __name__ == "__main__":
    print("🛠️ CREATING MULTI-SKILL TEMPLATE")
    print("=" * 40)
    
    template = test_multi_skill_template()
    
    print(f"\n✅ Multi-skill template ready!")
    print("   File: templates/multi_skill_fixed.yaml")
    print("   Combines: General + Technical + Code + Medical + Professional")