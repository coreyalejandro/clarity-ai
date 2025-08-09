"""
Compare data generation methods:
1. Basic template method
2. CoT-Self-Instruct method (from paper)
"""
import json
import sys
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def analyze_dataset(file_path, method_name):
    """Analyze quality of a dataset"""
    print(f"\n📊 {method_name} Analysis:")
    print("="*40)
    
    try:
        with open(file_path, 'r') as f:
            samples = [json.loads(line)['text'] for line in f]
        
        template = Template.from_yaml("templates/demo.yaml")
        scores = []
        
        for sample in samples[:10]:  # Test first 10
            score = template.evaluate(sample)
            scores.append(score)
        
        avg_score = sum(scores) / len(scores)
        
        print(f"📈 Sample count: {len(samples)}")
        print(f"📊 Average score: {avg_score:.3f}")
        print(f"📉 Min score: {min(scores):.3f}")
        print(f"📈 Max score: {max(scores):.3f}")
        
        # Show quality distribution
        high_quality = len([s for s in scores if s >= 0.7])
        medium_quality = len([s for s in scores if 0.4 <= s < 0.7])
        low_quality = len([s for s in scores if s < 0.4])
        
        print(f"🎯 High quality (≥0.7): {high_quality}")
        print(f"⚠️  Medium quality (0.4-0.7): {medium_quality}")
        print(f"❌ Low quality (<0.4): {low_quality}")
        
        # Show sample examples
        print(f"\n📝 Example samples:")
        best_idx = scores.index(max(scores))
        worst_idx = scores.index(min(scores))
        
        print(f"   Best ({scores[best_idx]:.3f}): '{samples[best_idx][:60]}...'")
        print(f"   Worst ({scores[worst_idx]:.3f}): '{samples[worst_idx][:60]}...'")
        
        return {
            'method': method_name,
            'count': len(samples),
            'avg_score': avg_score,
            'min_score': min(scores),
            'max_score': max(scores),
            'quality_dist': {
                'high': high_quality,
                'medium': medium_quality,
                'low': low_quality
            }
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return None

def main():
    print("🔍 COMPARING DATA GENERATION METHODS")
    print("="*60)
    
    # Analyze basic template method
    basic_results = analyze_dataset(
        "datasets/clarity_training/train.jsonl", 
        "BASIC TEMPLATE METHOD"
    )
    
    # Analyze CoT method
    cot_results = analyze_dataset(
        "datasets/clarity_training/cot_train.jsonl",
        "CoT-SELF-INSTRUCT METHOD"
    )
    
    # Comparison
    if basic_results and cot_results:
        print(f"\n🏆 METHOD COMPARISON:")
        print("="*40)
        
        print(f"📊 Sample Count:")
        print(f"   Basic: {basic_results['count']}")
        print(f"   CoT: {cot_results['count']}")
        
        print(f"\n📈 Average Quality:")
        print(f"   Basic: {basic_results['avg_score']:.3f}")
        print(f"   CoT: {cot_results['avg_score']:.3f}")
        
        improvement = cot_results['avg_score'] - basic_results['avg_score']
        improvement_pct = (improvement / basic_results['avg_score']) * 100
        
        if improvement > 0:
            print(f"✅ CoT Improvement: +{improvement:.3f} ({improvement_pct:+.1f}%)")
        else:
            print(f"❌ CoT Decline: {improvement:.3f} ({improvement_pct:+.1f}%)")
        
        print(f"\n🎯 High Quality Samples:")
        print(f"   Basic: {basic_results['quality_dist']['high']}/10")
        print(f"   CoT: {cot_results['quality_dist']['high']}/10")
        
        # Recommendation
        if cot_results['avg_score'] > basic_results['avg_score']:
            print(f"\n🏆 RECOMMENDATION: Use CoT-Self-Instruct method!")
            print("   Higher quality and better distribution")
        else:
            print(f"\n🏆 RECOMMENDATION: Use Basic Template method")
            print("   Higher average scores")

if __name__ == "__main__":
    main()