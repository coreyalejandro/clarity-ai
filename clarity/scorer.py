import re
import yaml
from typing import Dict, Any, Union, List
from dataclasses import dataclass
import os

# Import advanced rules
try:
    from .advanced_rules import create_advanced_rule, ADVANCED_RULE_TYPES, RuleExplanation
    ADVANCED_RULES_AVAILABLE = True
except ImportError:
    ADVANCED_RULES_AVAILABLE = False
    RuleExplanation = None


@dataclass
class Rule:
    """A single scoring rule with a type and parameters."""
    
    rule_type: str
    weight: float
    params: Dict[str, Any]
    
    def evaluate(self, text: str) -> float:
        """Evaluate this rule against the given text.
        
        Returns:
            float: Score between 0.0 and 1.0
        """
        # Check if this is an advanced rule type
        if ADVANCED_RULES_AVAILABLE and self.rule_type in ADVANCED_RULE_TYPES:
            try:
                advanced_rule = create_advanced_rule(self.rule_type, self.weight, self.params)
                return advanced_rule.evaluate(text)
            except Exception as e:
                print(f"Warning: Advanced rule {self.rule_type} failed: {e}")
                return 0.0
        
        # Basic rule types
        if self.rule_type == "regex_match":
            pattern = self.params.get("pattern", "")
            if re.search(pattern, text, re.IGNORECASE):
                return 1.0
            return 0.0
            
        elif self.rule_type == "contains_phrase":
            phrase = self.params.get("phrase", "")
            if phrase.lower() in text.lower():
                return 1.0
            return 0.0
            
        elif self.rule_type == "cosine_sim":
            # Simple word overlap for MVP - will enhance with sentence transformers later
            target = self.params.get("target", "")
            text_words = set(text.lower().split())
            target_words = set(target.lower().split())
            if len(target_words) == 0:
                return 0.0
            overlap = len(text_words.intersection(target_words))
            return min(1.0, overlap / len(target_words))
        
        elif self.rule_type == "word_count":
            min_words = self.params.get("min_words", 0)
            max_words = self.params.get("max_words", float('inf'))
            word_count = len(text.split())
            if min_words <= word_count <= max_words:
                return 1.0
            return 0.0
        
        elif self.rule_type == "sentiment_positive":
            # Simple positive word detection for MVP
            positive_words = ["good", "great", "excellent", "positive", "helpful", "clear"]
            text_lower = text.lower()
            matches = sum(1 for word in positive_words if word in text_lower)
            return min(1.0, matches / 3.0)  # Scale to 0-1
            
        else:
            raise ValueError(f"Unknown rule type: {self.rule_type}")
    
    def evaluate_with_explanation(self, text: str) -> Dict[str, Any]:
        """Evaluate with detailed explanation (for advanced rules)."""
        # Check if this is an advanced rule type
        if ADVANCED_RULES_AVAILABLE and self.rule_type in ADVANCED_RULE_TYPES:
            try:
                advanced_rule = create_advanced_rule(self.rule_type, self.weight, self.params)
                explanation = advanced_rule.evaluate_with_explanation(text)
                return {
                    "rule_type": self.rule_type,
                    "weight": self.weight,
                    "raw_score": explanation.score,
                    "weighted_score": explanation.score * self.weight,
                    "reasoning": explanation.reasoning,
                    "evidence": explanation.evidence,
                    "confidence": explanation.confidence,
                    "suggestions": explanation.suggestions,
                    "params": self.params
                }
            except Exception as e:
                return {
                    "rule_type": self.rule_type,
                    "weight": self.weight,
                    "error": str(e),
                    "params": self.params
                }
        
        # Basic rule - provide simple explanation
        score = self.evaluate(text)
        return {
            "rule_type": self.rule_type,
            "weight": self.weight,
            "raw_score": score,
            "weighted_score": score * self.weight,
            "reasoning": f"Basic {self.rule_type} rule evaluation",
            "evidence": [f"Score: {score}"],
            "confidence": 0.8,
            "suggestions": [],
            "params": self.params
        }


class Template:
    """A collection of scoring rules that can be applied to text."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.rules: List[Rule] = []
        self.description = ""
    
    def add_rule(self, rule_type: str, weight: float, **params):
        """Add a new rule to this template.
        
        Args:
            rule_type: Type of rule (regex_match, contains_phrase, cosine_sim, word_count, sentiment_positive)
            weight: How much this rule counts toward final score
            **params: Rule-specific parameters
        """
        rule = Rule(rule_type=rule_type, weight=weight, params=params)
        self.rules.append(rule)
    
    def evaluate(self, text: str) -> float:
        """Evaluate all rules against the text and return weighted average.
        
        Returns:
            float: Final score between 0.0 and 1.0
        """
        if not self.rules:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for rule in self.rules:
            try:
                rule_score = rule.evaluate(text)
                total_score += rule_score * rule.weight
                total_weight += rule.weight
            except Exception as e:
                print(f"Warning: Rule {rule.rule_type} failed with error: {e}")
                continue
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def evaluate_detailed(self, text: str) -> Dict[str, Any]:
        """Evaluate with detailed breakdown of each rule's contribution."""
        if not self.rules:
            return {"total_score": 0.0, "rule_scores": []}
        
        rule_scores = []
        total_score = 0.0
        total_weight = 0.0
        
        for rule in self.rules:
            try:
                rule_score = rule.evaluate(text)
                weighted_score = rule_score * rule.weight
                total_score += weighted_score
                total_weight += rule.weight
                
                rule_scores.append({
                    "rule_type": rule.rule_type,
                    "weight": rule.weight,
                    "raw_score": rule_score,
                    "weighted_score": weighted_score,
                    "params": rule.params
                })
            except Exception as e:
                rule_scores.append({
                    "rule_type": rule.rule_type,
                    "weight": rule.weight,
                    "error": str(e),
                    "params": rule.params
                })
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        return {
            "total_score": final_score,
            "total_weight": total_weight,
            "rule_scores": rule_scores
        }
    
    def evaluate_with_explanations(self, text: str) -> Dict[str, Any]:
        """Evaluate with rich explanations and actionable feedback."""
        if not self.rules:
            return {
                "total_score": 0.0,
                "rule_explanations": [],
                "overall_feedback": {
                    "strengths": [],
                    "weaknesses": ["No evaluation rules defined"],
                    "suggestions": ["Add scoring rules to evaluate text quality"]
                }
            }
        
        rule_explanations = []
        total_score = 0.0
        total_weight = 0.0
        all_suggestions = []
        strengths = []
        weaknesses = []
        
        for rule in self.rules:
            explanation = rule.evaluate_with_explanation(text)
            rule_explanations.append(explanation)
            
            if "error" not in explanation:
                total_score += explanation["weighted_score"]
                total_weight += explanation["weight"]
                
                # Collect feedback
                if explanation["raw_score"] >= 0.7:
                    strengths.append(f"{explanation['rule_type']}: {explanation['reasoning']}")
                elif explanation["raw_score"] < 0.4:
                    weaknesses.append(f"{explanation['rule_type']}: {explanation['reasoning']}")
                
                all_suggestions.extend(explanation.get("suggestions", []))
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Generate overall feedback
        overall_feedback = {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": list(set(all_suggestions)),  # Remove duplicates
            "score_interpretation": self._interpret_score(final_score)
        }
        
        return {
            "total_score": final_score,
            "total_weight": total_weight,
            "rule_explanations": rule_explanations,
            "overall_feedback": overall_feedback
        }
    
    def _interpret_score(self, score: float) -> str:
        """Provide human-readable interpretation of the score."""
        if score >= 0.9:
            return "Excellent - text meets or exceeds all quality criteria"
        elif score >= 0.7:
            return "Good - text meets most quality criteria with minor areas for improvement"
        elif score >= 0.5:
            return "Moderate - text meets some criteria but has significant room for improvement"
        elif score >= 0.3:
            return "Poor - text fails to meet most quality criteria and needs substantial revision"
        else:
            return "Very Poor - text fails to meet basic quality standards and requires complete revision"
    
    @classmethod
    def from_yaml(cls, yaml_path: str):
        """Load a template from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Template file not found: {yaml_path}")
        
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        template = cls(name=data.get('name', 'default'))
        template.description = data.get('description', '')
        
        for rule_data in data.get('rules', []):
            template.add_rule(
                rule_type=rule_data['type'],
                weight=rule_data.get('weight', 1.0),
                **rule_data.get('params', {})
            )
        
        return template
    
    def to_yaml(self, yaml_path: str):
        """Save this template to a YAML file."""
        data = {
            'name': self.name,
            'description': self.description,
            'rules': []
        }
        
        for rule in self.rules:
            rule_data = {
                'type': rule.rule_type,
                'weight': rule.weight,
                'params': rule.params
            }
            data['rules'].append(rule_data)
        
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)


def score(text: str, template: Union[str, Template]) -> float:
    """Main scoring function - the public API.
    
    Args:
        text: Text to evaluate
        template: Template object or path to YAML template file
    
    Returns:
        float: Score between 0.0 and 1.0
    """
    if isinstance(template, str):
        template = Template.from_yaml(template)
    
    return template.evaluate(text)


def score_detailed(text: str, template: Union[str, Template]) -> Dict[str, Any]:
    """Detailed scoring function with rule-by-rule breakdown.
    
    Args:
        text: Text to evaluate
        template: Template object or path to YAML template file
    
    Returns:
        Dict with total score and detailed rule breakdown
    """
    if isinstance(template, str):
        template = Template.from_yaml(template)
    
    return template.evaluate_detailed(text)