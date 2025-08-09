"""
Custom reward function for Axolotl that uses ClarityAI scoring
"""
import sys
import os
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')

from clarity.scorer import Template

def load_template():
    template_path = "templates/demo.yaml"
    return Template.from_yaml(template_path)

def compute_reward(generated_text):
    """Compute reward using ClarityAI template"""
    try:
        template = load_template()
        score = template.evaluate(generated_text)
        return score
    except Exception as e:
        print(f"Error computing reward: {e}")
        return 0.0

if __name__ == "__main__":
    # Test the reward function
    test_text = "This is a helpful guide with clear examples"
    reward = compute_reward(test_text)
    print(f"Test reward: {reward}")