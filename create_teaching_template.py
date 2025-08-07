"""
Create a multi-skill template based on teaching principles for autistic students
Using explicit rubric structure with clear, measurable criteria
"""
import sys
import json
import os
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def create_teaching_based_template():
    """Create template based on special education teaching principles"""
    
    template = Template("teaching_multi_skill")
    
    # STRUCTURE: Clear step-by-step organization (autism-friendly)
    structure_phrases = [
        "first", "second", "third", "next", "then", "finally",
        "step 1", "step 2", "step 3", "step-by-step",
        "begin by", "start with", "follow these steps",
        "here's how", "the process", "sequence", "order"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=4.0,  # Highest weight - structure is critical
        phrases=structure_phrases,
        min_matches=2
    )
    
    # EXPLICIT EXAMPLES: Concrete, specific examples (not abstract)
    example_phrases = [
        "for example", "such as", "like this", "here's an example",
        "specifically", "in particular", "instance", "case study",
        "demonstrated by", "illustrated by", "shown in", "example:"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=3.5,
        phrases=example_phrases,
        min_matches=1
    )
    
    # ACTIONABLE INSTRUCTIONS: Clear what-to-do language
    action_phrases = [
        "you should", "you can", "you need to", "you must",
        "do this", "follow this", "use this", "apply this",
        "implement", "configure", "setup", "install", "create",
        "write", "code", "build", "design", "test", "check"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=3.0,
        phrases=action_phrases,
        min_matches=2
    )
    
    # SAFETY/WARNING STRUCTURE: Explicit cautions (critical for medical/technical)
    safety_phrases = [
        "important:", "warning:", "caution:", "note:", "remember:",
        "always", "never", "don't", "avoid", "ensure", "make sure",
        "be careful", "pay attention", "double-check", "verify"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=3.0,
        phrases=safety_phrases,
        min_matches=1
    )
    
    # COMPLETION CRITERIA: Clear success measures
    completion_phrases = [
        "you'll know it's working when", "success looks like", "completed when",
        "finished if", "done correctly", "properly configured", "working properly",
        "should result in", "expect to see", "indicates success"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.5,
        phrases=completion_phrases,
        min_matches=1
    )
    
    # MULTI-DOMAIN VOCABULARY: Shows cross-skill knowledge
    multi_domain_phrases = [
        # Medical + Technical
        "healthcare system", "medical device", "patient data", "HIPAA compliance",
        # Code + Professional  
        "documentation standards", "code review", "best practices", "industry standards",
        # Technical + Safety
        "security protocol", "backup procedure", "disaster recovery", "risk assessment",
        # General + Specific
        "practical implementation", "real-world application", "professional context"
    ]
    
    template.add_rule(
        "contains_phrase",
        weight=2.0,
        phrases=multi_domain_phrases,
        min_matches=1
    )
    
    # APPROPRIATE LENGTH: Comprehensive but not overwhelming
    template.add_rule(
        "word_count",
        weight=2.0,
        min_words=50,  # More detailed than single-skill
        max_words=300  # Not overwhelming
    )
    
    # POSITIVE LEARNING TONE: Encouraging, not intimidating
    template.add_rule(
        "sentiment_positive",
        weight=1.5,
        min_score=0.2  # Slightly positive, supportive tone
    )
    
    return template

def test_teaching_template():
    """Test with teaching-principle based content"""
    
    template = create_teaching_based_template()
    template.to_yaml("templates/teaching_multi_skill.yaml")
    
    print("🎯 Created Teaching-Based Multi-Skill Template")
    print(f"   Rules: {len(template.rules)}")
    print("   Based on: Autism education + explicit rubrics")
    
    # Test samples based on teaching principles
    test_samples = {
        "poor_structure": "Database stuff is important. You should learn it. It's useful for things.",
        
        "basic_helpful": "This guide provides clear information about database optimization with practical examples.",
        
        "good_teaching_structure": "Here's how to optimize your database step-by-step. First, analyze query performance using execution plans. For example, slow SELECT statements often need index optimization. You should start by identifying the most frequently used queries. Important: Always backup your database before making changes. You'll know it's working when query response times improve significantly.",
        
        "excellent_multi_skill": "Follow these steps to implement secure database optimization for healthcare applications. First, ensure HIPAA compliance by reviewing security protocols and patient data access controls. Step 1: Configure proper authentication with role-based permissions. For example, read-only access for reporting staff, full access for database administrators. Important: Never store passwords in plain text - always use encrypted authentication. Step 2: Implement performance monitoring with automated alerting. You should setup query execution tracking and establish baseline performance metrics. Warning: Changes to production systems require proper change management procedures. Step 3: Create backup and disaster recovery procedures following industry best practices. You'll know the implementation is successful when security audits pass, performance metrics improve, and compliance requirements are met. Remember: Always consult with your security team and healthcare compliance officers before implementing changes to patient data systems."
    }
    
    print(f"\n🧪 Testing Teaching-Based Template:")
    
    from clarity.scorer import score
    
    for name, content in test_samples.items():
        sample_score = score(content, template)
        print(f"   {name}: {sample_score:.3f}")
        if name == "excellent_multi_skill":
            print(f"      (Should score highest - uses teaching principles)")
    
    return template

def create_teaching_training_data():
    """Create training data using explicit teaching structure"""
    
    print(f"\n📚 Creating Teaching-Structured Training Data:")
    
    teaching_samples = [
        {
            "text": "Follow these steps to implement secure API development for medical applications. Step 1: Begin by reviewing HIPAA compliance requirements and establishing security protocols. For example, all patient data must be encrypted both in transit and at rest. Important: Never log sensitive patient information in application logs. Step 2: Configure authentication using industry-standard OAuth 2.0 with proper token management. You should implement role-based access controls where doctors have different permissions than administrative staff. Step 3: Setup comprehensive error handling that doesn't expose sensitive information. Warning: Generic error messages prevent information leakage but maintain user experience. You'll know your implementation is successful when security audits pass, API response times remain under 200ms, and healthcare compliance requirements are met. Remember: Always consult with your legal and compliance teams before deploying medical data systems."
        },
        {
            "text": "Here's how to create effective technical documentation step-by-step. First, start with clear learning objectives - what should readers accomplish after reading? For example, 'Users will be able to configure SSL certificates for production deployment.' Step 1: Write an overview that explains the purpose and context. You should include prerequisites and expected completion time. Step 2: Break complex procedures into numbered steps with specific actions. For instance, 'Run the following command: sudo systemctl restart nginx' rather than 'restart the web server.' Important: Always include troubleshooting sections for common issues. Step 3: Provide working code examples with proper syntax highlighting and explanations. Warning: Test all code examples in a clean environment before publishing. You'll know your documentation is effective when new team members can follow it independently and achieve the stated objectives. Remember: Update documentation immediately when procedures change to maintain accuracy."
        },
        {
            "text": "Follow these steps to optimize database performance while maintaining data integrity and security. Step 1: Begin by establishing baseline performance metrics using monitoring tools. For example, track average query execution time, connection pool usage, and resource consumption. Important: Never optimize production databases without proper backups and rollback procedures. Step 2: Analyze slow query logs to identify performance bottlenecks. You should focus on queries that run frequently or consume significant resources. For instance, SELECT statements without proper WHERE clauses often cause table scans. Step 3: Implement index optimization based on query patterns and data access requirements. Warning: Over-indexing can slow INSERT and UPDATE operations, so balance read and write performance. Step 4: Configure connection pooling and caching strategies appropriate for your application load. You'll know optimization is successful when query response times improve by at least 20%, resource utilization decreases, and application performance monitoring shows consistent improvements. Remember: Always test performance changes in staging environments before production deployment."
        }
    ]
    
    import os
    os.makedirs('datasets/teaching_multi_skill', exist_ok=True)
    
    with open('datasets/teaching_multi_skill/train.jsonl', 'w') as f:
        for sample in teaching_samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"✅ Created {len(teaching_samples)} teaching-structured samples")
    print("📋 Each uses: Steps + Examples + Warnings + Success Criteria")
    
    return len(teaching_samples)

if __name__ == "__main__":
    print("🎓 CREATING TEACHING-BASED MULTI-SKILL TEMPLATE")
    print("Based on special education principles for autistic students")
    print("=" * 60)
    
    template = test_teaching_template()
    sample_count = create_teaching_training_data()
    
    print(f"\n✅ TEACHING TEMPLATE COMPLETE!")
    print("Key principles applied:")
    print("• Explicit structure (step-by-step)")
    print("• Concrete examples (not abstract)")
    print("• Clear actionable instructions")
    print("• Safety/warning structure")
    print("• Success criteria definition")
    print("• Multi-domain vocabulary integration")
    
    print(f"\n🚀 Ready for Experiment 4 (Revised) with teaching approach!")