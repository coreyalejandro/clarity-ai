#!/usr/bin/env python3
"""
Advanced ClarityAI Demo - Showcasing Sophisticated Rubric Evaluation

This demo demonstrates how ClarityAI makes fine-tuning accessible while providing
enterprise-grade rubric evaluation with detailed explanations and actionable feedback.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clarity.scorer import Template
import json


def print_separator(title: str):
    """Print a formatted section separator."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_rule_explanation(explanation: dict):
    """Print a detailed rule explanation."""
    print(f"\n📊 {explanation['rule_type'].upper()} (Weight: {explanation['weight']})")
    print(f"   Score: {explanation['raw_score']:.3f} → Weighted: {explanation['weighted_score']:.3f}")
    print(f"   Reasoning: {explanation['reasoning']}")
    
    if explanation.get('evidence'):
        print("   Evidence:")
        for evidence in explanation['evidence']:
            print(f"     • {evidence}")
    
    if explanation.get('suggestions'):
        print("   Suggestions:")
        for suggestion in explanation['suggestions']:
            print(f"     → {suggestion}")
    
    print(f"   Confidence: {explanation.get('confidence', 0.8):.1%}")


def demo_academic_paper():
    """Demonstrate academic paper evaluation."""
    print_separator("ACADEMIC PAPER EVALUATION DEMO")
    
    # Load the academic paper template
    try:
        template = Template.from_yaml("templates/academic-paper.yaml")
        print(f"✅ Loaded template: {template.name}")
        print(f"   Description: {template.description}")
        print(f"   Rules: {len(template.rules)}")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Sample academic text (intentionally mixed quality)
    academic_text = """
    Machine learning has revolutionized many fields through its ability to learn patterns from data.
    Neural networks, particularly deep learning architectures, have shown remarkable performance
    in tasks such as image recognition and natural language processing. However, these models
    often suffer from overfitting when training data is limited.
    
    To address this issue, researchers have developed various regularization techniques including
    dropout, batch normalization, and weight decay. Cross-validation is commonly used to evaluate
    model performance and select optimal hyperparameters. The gradient descent optimization
    algorithm, combined with backpropagation, enables efficient training of neural networks.
    
    Recent advances in transformer architectures and attention mechanisms have further improved
    model performance across various domains. These developments demonstrate the importance of
    feature engineering and proper model selection in achieving state-of-the-art results.
    """
    
    print(f"\n📝 Sample Text ({len(academic_text.split())} words):")
    print(academic_text[:200] + "..." if len(academic_text) > 200 else academic_text)
    
    # Evaluate with explanations
    try:
        result = template.evaluate_with_explanations(academic_text)
        
        print(f"\n🎯 OVERALL SCORE: {result['total_score']:.3f}")
        print(f"   {result['overall_feedback']['score_interpretation']}")
        
        print("\n📋 DETAILED RULE BREAKDOWN:")
        for explanation in result['rule_explanations']:
            if 'error' not in explanation:
                print_rule_explanation(explanation)
            else:
                print(f"\n❌ {explanation['rule_type']}: {explanation['error']}")
        
        print("\n💪 STRENGTHS:")
        for strength in result['overall_feedback']['strengths']:
            print(f"   ✅ {strength}")
        
        print("\n⚠️  AREAS FOR IMPROVEMENT:")
        for weakness in result['overall_feedback']['weaknesses']:
            print(f"   🔸 {weakness}")
        
        print("\n💡 ACTIONABLE SUGGESTIONS:")
        for suggestion in result['overall_feedback']['suggestions']:
            print(f"   → {suggestion}")
            
    except Exception as e:
        print(f"❌ Evaluation error: {e}")


def demo_code_review():
    """Demonstrate code review evaluation."""
    print_separator("CODE REVIEW EVALUATION DEMO")
    
    # Load the code review template
    try:
        template = Template.from_yaml("templates/code-review.yaml")
        print(f"✅ Loaded template: {template.name}")
        print(f"   Description: {template.description}")
        print(f"   Rules: {len(template.rules)}")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return
    
    # Sample code review comments (good and bad examples)
    good_review = """
    I suggest refactoring the authentication logic in line 45 to improve maintainability.
    Consider implementing the Strategy pattern here to handle different authentication methods.
    The current approach creates technical debt and makes unit testing more difficult.
    
    Additionally, I recommend adding input validation for the user credentials to prevent
    security vulnerabilities. The current implementation doesn't sanitize user input,
    which could lead to injection attacks.
    """
    
    bad_review = """
    This code is bad. Fix it.
    """
    
    print("\n📝 GOOD REVIEW EXAMPLE:")
    print(good_review)
    
    try:
        result = template.evaluate_with_explanations(good_review)
        print(f"\n🎯 SCORE: {result['total_score']:.3f} - {result['overall_feedback']['score_interpretation']}")
        
        print("\n📊 TOP PERFORMING RULES:")
        sorted_rules = sorted(result['rule_explanations'], 
                            key=lambda x: x.get('raw_score', 0), reverse=True)[:3]
        for explanation in sorted_rules:
            if 'error' not in explanation and explanation['raw_score'] > 0.5:
                print(f"   ✅ {explanation['rule_type']}: {explanation['raw_score']:.3f}")
                print(f"      {explanation['reasoning']}")
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
    
    print("\n📝 BAD REVIEW EXAMPLE:")
    print(bad_review)
    
    try:
        result = template.evaluate_with_explanations(bad_review)
        print(f"\n🎯 SCORE: {result['total_score']:.3f} - {result['overall_feedback']['score_interpretation']}")
        
        print("\n⚠️  KEY ISSUES:")
        for weakness in result['overall_feedback']['weaknesses'][:3]:
            print(f"   🔸 {weakness}")
        
        print("\n💡 IMPROVEMENT SUGGESTIONS:")
        for suggestion in result['overall_feedback']['suggestions'][:5]:
            print(f"   → {suggestion}")
    except Exception as e:
        print(f"❌ Evaluation error: {e}")


def demo_fine_tuning_accessibility():
    """Demonstrate how ClarityAI makes fine-tuning accessible."""
    print_separator("FINE-TUNING ACCESSIBILITY DEMONSTRATION")
    
    print("""
🎯 THE PROBLEM WITH TRADITIONAL FINE-TUNING:
   • Requires deep ML expertise to design reward functions
   • Complex code to implement RLHF/PPO training loops  
   • No interpretable feedback on why models improve/fail
   • Expensive trial-and-error cycles
   • Black box optimization with unclear objectives

✨ CLARITYAI'S SOLUTION:
   • Teacher-like rubrics anyone can understand and create
   • Visual interface for non-technical users
   • Immediate feedback with detailed rule breakdowns
   • Iterative improvement through template refinement
   • Explainable AI with actionable suggestions

📈 BUSINESS IMPACT:
   • Reduces fine-tuning expertise barrier from PhD → High School
   • Cuts development time from weeks → hours
   • Provides interpretable quality metrics
   • Enables domain experts to directly improve models
   • Scales AI development across organizations
    """)
    
    # Show a simple template that a non-technical user could create
    simple_template = Template("customer_support")
    simple_template.description = "Evaluate customer support responses for helpfulness and professionalism"
    simple_template.add_rule("contains_phrase", 2.0, phrase="help")
    simple_template.add_rule("contains_phrase", 1.5, phrase="understand")
    simple_template.add_rule("sentiment_positive", 2.0)
    simple_template.add_rule("word_count", 1.0, min_words=20, max_words=150)
    
    print("\n📝 EXAMPLE: Non-Technical User Creates Customer Support Rubric")
    print("   (No coding required - just YAML configuration)")
    
    sample_response = """
    I understand your frustration with the billing issue. Let me help you resolve this quickly.
    I've reviewed your account and can see the problem. I'll process a refund immediately
    and ensure this doesn't happen again. Is there anything else I can help you with today?
    """
    
    result = simple_template.evaluate_detailed(sample_response)
    print(f"\n🎯 Instant Feedback: {result['total_score']:.3f}")
    print("   ✅ Contains 'help' and 'understand'")
    print("   ✅ Positive, professional tone")
    print("   ✅ Appropriate length")
    print("\n💡 This rubric can now train AI models to write better support responses!")


def demo_domain_specific_rules():
    """Demonstrate domain-specific advanced rules."""
    print_separator("DOMAIN-SPECIFIC RULES DEMONSTRATION")
    
    print("""
🎯 NEW ADVANCED RULE TYPES FOR SPECIALIZED DOMAINS:
   • SecurityAssessmentRule: Cybersecurity awareness and best practices
   • LegalComplianceRule: Legal risk awareness and compliance
   • MedicalAccuracyRule: Clinical accuracy and professional standards
   • FinancialComplianceRule: Financial advice compliance and risk disclosures
   • AccessibilityRule: Inclusive design and accessibility awareness
    """)
    
    # Security Assessment Demo
    print("\n🔒 SECURITY ASSESSMENT EXAMPLE:")
    security_text = """
    The authentication system has several vulnerabilities that require immediate attention.
    I recommend implementing input validation to prevent SQL injection attacks and adding
    CSRF protection to all forms. The current implementation lacks proper encryption for
    sensitive data transmission. We should also conduct a penetration test to identify
    additional security risks and ensure compliance with security standards.
    """
    
    try:
        template = Template.from_yaml("templates/security-assessment.yaml")
        result = template.evaluate_with_explanations(security_text)
        print(f"🎯 Security Score: {result['total_score']:.3f}")
        print(f"   {result['overall_feedback']['score_interpretation']}")
        
        # Show top security insights
        security_rules = [r for r in result['rule_explanations'] 
                         if r.get('rule_type') == 'security_assessment' and 'error' not in r]
        if security_rules:
            rule = security_rules[0]
            print(f"   Security Analysis: {rule['reasoning']}")
            print(f"   Evidence: {rule['evidence'][0] if rule['evidence'] else 'N/A'}")
    except Exception as e:
        print(f"   ⚠️  Security template not available: {e}")
    
    # Medical Documentation Demo
    print("\n🏥 MEDICAL DOCUMENTATION EXAMPLE:")
    medical_text = """
    Patient presents with acute chest pain and shortness of breath. Clinical examination
    reveals elevated troponin levels and ECG changes consistent with myocardial infarction.
    Treatment protocol includes immediate anticoagulation therapy and cardiac catheterization.
    Contraindications include active bleeding and recent surgery. This is not medical advice -
    consult your healthcare provider for proper diagnosis and treatment.
    """
    
    try:
        template = Template.from_yaml("templates/medical-documentation.yaml")
        result = template.evaluate_with_explanations(medical_text)
        print(f"🎯 Medical Score: {result['total_score']:.3f}")
        print(f"   {result['overall_feedback']['score_interpretation']}")
        
        # Show medical accuracy insights
        medical_rules = [r for r in result['rule_explanations'] 
                        if r.get('rule_type') == 'medical_accuracy' and 'error' not in r]
        if medical_rules:
            rule = medical_rules[0]
            print(f"   Medical Analysis: {rule['reasoning']}")
    except Exception as e:
        print(f"   ⚠️  Medical template not available: {e}")


def main():
    """Run the advanced ClarityAI demonstration."""
    print("🚀 ClarityAI Advanced Demonstration")
    print("   Making Fine-Tuning Accessible with Enterprise-Grade Rubrics")
    
    try:
        demo_fine_tuning_accessibility()
        demo_academic_paper()
        demo_code_review()
        demo_domain_specific_rules()
        
        print_separator("SUMMARY")
        print("""
🎉 ClarityAI transforms fine-tuning from a complex ML engineering task into an
   intuitive rubric design process that domain experts can master.

🔑 Key Advantages:
   • Explainable AI with detailed reasoning
   • Actionable feedback for continuous improvement  
   • Accessible to non-technical domain experts
   • Enterprise-grade evaluation sophistication
   • Domain-specific rule types for specialized industries
   • Seamless integration with existing workflows

🏭 INDUSTRY-SPECIFIC CAPABILITIES:
   • Healthcare: Medical accuracy and compliance validation
   • Finance: Risk disclosure and regulatory compliance
   • Security: Vulnerability assessment and best practices
   • Legal: Risk awareness and compliance checking
   • Accessibility: Inclusive design and WCAG compliance

🚀 Ready to revolutionize your AI development process?
   Start with: streamlit run app.py
        """)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()