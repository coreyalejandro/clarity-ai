"""
Simple DSPy test to validate the integration with ClarityAI
"""
import dspy
import sys
import json
from datetime import datetime

sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def test_dspy_integration():
    """Test DSPy integration with ClarityAI scoring"""
    
    print("🧪 DSPy + ClarityAI Integration Test")
    print("=" * 50)
    
    # Create a proper DSPy LM
    class MockDSPyLM(dspy.LM):
        def __init__(self):
            super().__init__(model="mock-helpful-model")
        
        def basic_request(self, prompt, **kwargs):
            """Mock generation - returns a simple helpful response"""
            responses = [
                "This guide provides clear, step-by-step instructions with practical examples.",
                "Here's a comprehensive tutorial with detailed explanations and code samples.", 
                "Follow these proven methods to achieve your goals effectively.",
                "This resource contains actionable advice with clear implementation steps."
            ]
            import random
            return {"choices": [{"text": random.choice(responses)}]}
    
    # Configure DSPy with mock LM
    mock_lm = MockDSPyLM()
    dspy.configure(lm=mock_lm)
    
    # Define a simple signature for helpful content generation
    class HelpfulContentSignature(dspy.Signature):
        """Generate helpful, clear content"""
        
        topic = dspy.InputField(desc="Topic to write about")
        content = dspy.OutputField(desc="Helpful, clear content about the topic")
    
    # Create a simple DSPy module
    class HelpfulContentGenerator(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate = dspy.Predict(HelpfulContentSignature)
        
        def forward(self, topic):
            result = self.generate(topic=topic)
            return result.content
    
    # Test the generator
    generator = HelpfulContentGenerator()
    
    # Create ClarityAI metric
    template = Template.from_yaml("templates/demo.yaml")
    
    def clarity_metric(example, prediction):
        """Score using ClarityAI"""
        try:
            score = template.score(prediction)
            return score
        except Exception as e:
            print(f"Scoring error: {e}")
            return 0.0
    
    # Test topics
    test_topics = [
        "Python programming",
        "Web development",
        "Machine learning",
        "Database design"
    ]
    
    results = []
    total_score = 0
    
    print("\n🔬 Testing content generation...")
    for topic in test_topics:
        content = generator(topic=topic)
        score = clarity_metric(None, content)
        
        results.append({
            "topic": topic,
            "content": content,
            "score": score
        })
        
        total_score += score
        
        print(f"   📝 {topic}: {score:.3f}")
        print(f"      Content: {content[:80]}...")
    
    avg_score = total_score / len(test_topics)
    
    print(f"\n📊 Results Summary:")
    print(f"   Average ClarityAI Score: {avg_score:.3f}")
    print(f"   Total Topics Tested: {len(test_topics)}")
    
    # Save results
    results_data = {
        "experiment": "DSPy + ClarityAI Integration Test",
        "timestamp": datetime.now().isoformat(),
        "average_score": avg_score,
        "results": results
    }
    
    with open("dspy_integration_test_results.json", "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n✅ DSPy integration test complete!")
    print(f"📄 Results saved to: dspy_integration_test_results.json")
    
    # Show next steps
    print(f"\n🚀 Next Steps:")
    print("1. Replace mock LM with actual models (GPT-2, DialoGPT, etc.)")
    print("2. Use DSPy optimizers (BootstrapFewShot, COPRO, etc.)")
    print("3. Create task-specific signatures for code documentation")
    print("4. Integrate with model repurposing experiments")
    
    return results_data

if __name__ == "__main__":
    test_dspy_integration()