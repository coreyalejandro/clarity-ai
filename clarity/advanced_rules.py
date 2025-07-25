"""
Advanced rule types for sophisticated rubric evaluation.

This module provides enterprise-grade rule types that offer:
- Better explainability and interpretability
- More nuanced scoring mechanisms
- Domain-specific evaluation criteria
- Hierarchical rule composition
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from collections import Counter
from functools import lru_cache

# Optional dependencies with graceful fallbacks
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# Constants for scoring thresholds
DEFAULT_READABILITY_GRADE = 8
DEFAULT_READABILITY_TOLERANCE = 2
COHERENCE_HIGH_THRESHOLD = 0.7
COHERENCE_MEDIUM_THRESHOLD = 0.4
ARGUMENT_CLAIM_WEIGHT = 0.3
ARGUMENT_EVIDENCE_WEIGHT = 0.4
ARGUMENT_COUNTER_WEIGHT = 0.3
CITATION_LOW_DENSITY = 0.01
CITATION_MEDIUM_DENSITY = 0.05

# Domain-specific rule constants
SCORE_THRESHOLD_HIGH = 0.7
SCORE_THRESHOLD_MEDIUM = 0.4
CATEGORY_COVERAGE_WEIGHT = 0.7
TERM_DENSITY_WEIGHT = 0.3
TERM_DENSITY_MULTIPLIER = 10
MEDICAL_TERMINOLOGY_THRESHOLD = 0.3
FINANCIAL_TERMINOLOGY_THRESHOLD = 0.2
ACCESSIBILITY_PENALTY_PER_ISSUE = 0.1
MAX_ACCESSIBILITY_PENALTY = 0.5


@dataclass
class RuleExplanation:
    """Detailed explanation of why a rule produced its score."""
    rule_type: str
    score: float
    reasoning: str
    evidence: List[str]
    confidence: float
    suggestions: List[str]


class AdvancedRule:
    """Base class for advanced rules with rich explanations."""
    
    def __init__(self, rule_type: str, weight: float, params: Dict[str, Any]):
        self.rule_type = rule_type
        self.weight = weight
        self.params = params
        
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        """Evaluate text and return detailed explanation."""
        if not isinstance(text, str):
            raise TypeError(f"Expected string input, got {type(text)}")
        if not text.strip():
            return RuleExplanation(
                rule_type=self.rule_type,
                score=0.0,
                reasoning="Empty or whitespace-only text provided",
                evidence=["No content to evaluate"],
                confidence=1.0,
                suggestions=["Provide non-empty text for evaluation"]
            )
        raise NotImplementedError
        
    def evaluate(self, text: str) -> float:
        """Simple evaluation for backward compatibility."""
        try:
            return self.evaluate_with_explanation(text).score
        except Exception as e:
            # Log error and return neutral score
            print(f"Warning: Rule {self.rule_type} failed with error: {e}")
            return 0.5


class ReadabilityRule(AdvancedRule):
    """Evaluates text readability using multiple metrics."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        if not TEXTSTAT_AVAILABLE:
            return RuleExplanation(
                rule_type=self.rule_type,
                score=0.5,
                reasoning="textstat library not available for readability analysis",
                evidence=["Fallback scoring applied"],
                confidence=0.1,
                suggestions=["Install textstat: pip install textstat"]
            )
        
        target_grade = self.params.get('target_grade_level', DEFAULT_READABILITY_GRADE)
        tolerance = self.params.get('tolerance', DEFAULT_READABILITY_TOLERANCE)
        
        # Calculate readability metrics
        flesch_score = flesch_reading_ease(text)
        fk_grade = flesch_kincaid_grade(text)
        
        # Score based on grade level proximity
        grade_diff = abs(fk_grade - target_grade)
        if grade_diff <= tolerance:
            score = 1.0 - (grade_diff / tolerance) * 0.3
        else:
            score = max(0.0, 0.7 - (grade_diff - tolerance) * 0.1)
        
        # Generate explanation
        evidence = [
            f"Flesch Reading Ease: {flesch_score:.1f}",
            f"Flesch-Kincaid Grade Level: {fk_grade:.1f}",
            f"Target Grade Level: {target_grade}"
        ]
        
        if grade_diff <= tolerance:
            reasoning = f"Text readability is appropriate for target audience (grade {target_grade})"
            suggestions = []
        elif fk_grade > target_grade:
            reasoning = f"Text is too complex for target audience (grade {fk_grade:.1f} vs {target_grade})"
            suggestions = [
                "Use shorter sentences",
                "Replace complex words with simpler alternatives",
                "Break up long paragraphs"
            ]
        else:
            reasoning = f"Text may be too simple for target audience (grade {fk_grade:.1f} vs {target_grade})"
            suggestions = [
                "Add more sophisticated vocabulary",
                "Include more complex sentence structures",
                "Provide deeper analysis"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.9,
            suggestions=suggestions
        )


class SemanticCoherenceRule(AdvancedRule):
    """Evaluates semantic coherence and topic consistency."""
    
    def __init__(self, rule_type: str, weight: float, params: Dict[str, Any]):
        super().__init__(rule_type, weight, params)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic implementation if spaCy model not available
            self.nlp = None
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        if not self.nlp:
            return RuleExplanation(
                rule_type=self.rule_type,
                score=0.5,
                reasoning="SpaCy model not available for semantic analysis",
                evidence=["Fallback scoring applied"],
                confidence=0.1,
                suggestions=["Install spaCy English model: python -m spacy download en_core_web_sm"]
            )
        
        doc = self.nlp(text)
        sentences = list(doc.sents)
        
        if len(sentences) < 2:
            return RuleExplanation(
                rule_type=self.rule_type,
                score=0.8,
                reasoning="Single sentence - coherence not applicable",
                evidence=[f"Text contains {len(sentences)} sentence"],
                confidence=0.9,
                suggestions=[]
            )
        
        # Calculate sentence similarity matrix
        sentence_vectors = []
        for sent in sentences:
            if sent.vector_norm > 0:
                sentence_vectors.append(sent.vector)
            else:
                sentence_vectors.append(np.zeros(self.nlp.vocab.vectors_length))
        
        if len(sentence_vectors) < 2:
            score = 0.5
            reasoning = "Unable to compute sentence vectors for coherence analysis"
            evidence = ["Insufficient vector data"]
            suggestions = ["Use more descriptive language"]
        else:
            # Compute pairwise similarities more efficiently
            if SKLEARN_AVAILABLE:
                # Use sklearn's efficient implementation
                similarity_matrix = cosine_similarity(sentence_vectors)
                # Extract upper triangle (excluding diagonal)
                similarities = []
                for i in range(len(sentence_vectors)):
                    for j in range(i + 1, len(sentence_vectors)):
                        similarities.append(similarity_matrix[i][j])
            else:
                # Fallback to manual calculation
                similarities = []
                for i in range(len(sentence_vectors)):
                    for j in range(i + 1, len(sentence_vectors)):
                        # Manual cosine similarity calculation
                        vec_i = np.array(sentence_vectors[i])
                        vec_j = np.array(sentence_vectors[j])
                        dot_product = np.dot(vec_i, vec_j)
                        norm_i = np.linalg.norm(vec_i)
                        norm_j = np.linalg.norm(vec_j)
                        if norm_i > 0 and norm_j > 0:
                            sim = dot_product / (norm_i * norm_j)
                        else:
                            sim = 0.0
                        similarities.append(sim)
            
            avg_similarity = np.mean(similarities) if similarities else 0.0
            score = min(1.0, max(0.0, avg_similarity * 2))  # Scale to 0-1
            
            evidence = [
                f"Average sentence similarity: {avg_similarity:.3f}",
                f"Number of sentences analyzed: {len(sentences)}",
                f"Similarity range: {min(similarities):.3f} - {max(similarities):.3f}"
            ]
            
            if score >= COHERENCE_HIGH_THRESHOLD:
                reasoning = "Text shows strong semantic coherence between sentences"
                suggestions = []
            elif score >= COHERENCE_MEDIUM_THRESHOLD:
                reasoning = "Text shows moderate semantic coherence with some topic drift"
                suggestions = [
                    "Strengthen connections between sentences",
                    "Use more consistent terminology",
                    "Add transitional phrases"
                ]
            else:
                reasoning = "Text lacks semantic coherence - sentences seem disconnected"
                suggestions = [
                    "Focus on a single main topic",
                    "Add clear topic sentences",
                    "Remove off-topic content",
                    "Use consistent vocabulary throughout"
                ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.8,
            suggestions=suggestions
        )


class ArgumentStructureRule(AdvancedRule):
    """Evaluates logical argument structure and flow."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        # Look for argument indicators
        claim_indicators = ['therefore', 'thus', 'hence', 'consequently', 'as a result']
        evidence_indicators = ['because', 'since', 'given that', 'due to', 'for example', 'such as']
        counter_indicators = ['however', 'but', 'although', 'despite', 'on the other hand']
        
        text_lower = text.lower()
        
        claim_count = sum(1 for indicator in claim_indicators if indicator in text_lower)
        evidence_count = sum(1 for indicator in evidence_indicators if indicator in text_lower)
        counter_count = sum(1 for indicator in counter_indicators if indicator in text_lower)
        
        # Score based on argument structure
        structure_score = 0.0
        evidence = []
        suggestions = []
        
        # Check for claims
        if claim_count > 0:
            structure_score += ARGUMENT_CLAIM_WEIGHT
            evidence.append(f"Found {claim_count} claim indicators")
        else:
            suggestions.append("Add clear conclusions or claims (use 'therefore', 'thus', etc.)")
        
        # Check for evidence
        if evidence_count > 0:
            structure_score += ARGUMENT_EVIDENCE_WEIGHT
            evidence.append(f"Found {evidence_count} evidence indicators")
        else:
            suggestions.append("Provide supporting evidence (use 'because', 'for example', etc.)")
        
        # Check for balanced argumentation
        if counter_count > 0:
            structure_score += ARGUMENT_COUNTER_WEIGHT
            evidence.append(f"Found {counter_count} counter-argument indicators")
        else:
            suggestions.append("Consider counter-arguments (use 'however', 'although', etc.)")
        
        # Bonus for balanced structure
        if claim_count > 0 and evidence_count > 0:
            structure_score = min(1.0, structure_score + 0.1)
        
        if structure_score >= 0.8:
            reasoning = "Text demonstrates strong argumentative structure"
        elif structure_score >= 0.5:
            reasoning = "Text shows moderate argumentative structure"
        else:
            reasoning = "Text lacks clear argumentative structure"
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=structure_score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.7,
            suggestions=suggestions
        )


class DomainExpertiseRule(AdvancedRule):
    """Evaluates domain-specific expertise indicators."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        domain = self.params.get('domain', 'general')
        expertise_terms = self.params.get('expertise_terms', [])
        
        if not expertise_terms:
            return RuleExplanation(
                rule_type=self.rule_type,
                score=0.5,
                reasoning="No domain expertise terms specified",
                evidence=["Default scoring applied"],
                confidence=0.1,
                suggestions=["Configure domain-specific expertise terms"]
            )
        
        text_lower = text.lower()
        found_terms = []
        
        for term in expertise_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        # Score based on expertise term density
        term_density = len(found_terms) / len(text.split()) if text.split() else 0
        coverage_score = len(found_terms) / len(expertise_terms)
        
        # Combine density and coverage
        score = min(1.0, (term_density * 10 + coverage_score) / 2)
        
        evidence = [
            f"Domain expertise terms found: {len(found_terms)}/{len(expertise_terms)}",
            f"Term density: {term_density:.4f}",
            f"Found terms: {', '.join(found_terms) if found_terms else 'None'}"
        ]
        
        if score >= 0.7:
            reasoning = f"Text demonstrates strong {domain} domain expertise"
            suggestions = []
        elif score >= 0.4:
            reasoning = f"Text shows moderate {domain} domain knowledge"
            suggestions = [
                f"Include more {domain}-specific terminology",
                "Demonstrate deeper technical understanding",
                "Reference domain-specific concepts or frameworks"
            ]
        else:
            reasoning = f"Text lacks {domain} domain expertise indicators"
            suggestions = [
                f"Research and include {domain}-specific terms",
                "Consult domain experts for technical accuracy",
                "Add technical depth and specificity"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.8,
            suggestions=suggestions
        )


class CitationQualityRule(AdvancedRule):
    """Evaluates quality and appropriateness of citations."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        # Look for citation patterns
        citation_patterns = [
            r'\([A-Za-z]+,?\s+\d{4}\)',  # (Author, 2023)
            r'\[[0-9]+\]',               # [1]
            r'https?://[^\s]+',          # URLs
            r'doi:\s*[^\s]+',            # DOI
        ]
        
        citations_found = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citations_found.extend(matches)
        
        # Analyze citation quality
        citation_count = len(citations_found)
        word_count = len(text.split())
        citation_density = citation_count / word_count if word_count > 0 else 0
        
        # Score based on citation presence and density
        if citation_count == 0:
            score = 0.0
            reasoning = "No citations found in text"
            suggestions = [
                "Add credible sources to support claims",
                "Include academic references where appropriate",
                "Cite relevant research or documentation"
            ]
        elif citation_density < CITATION_LOW_DENSITY:
            score = 0.3
            reasoning = "Very few citations relative to text length"
            suggestions = [
                "Increase citation frequency for better support",
                "Cite sources for key claims and statistics"
            ]
        elif citation_density < CITATION_MEDIUM_DENSITY:
            score = 0.7
            reasoning = "Moderate citation density"
            suggestions = [
                "Consider adding more sources for comprehensive coverage"
            ]
        else:
            score = 1.0
            reasoning = "Good citation density and source support"
            suggestions = []
        
        evidence = [
            f"Citations found: {citation_count}",
            f"Citation density: {citation_density:.4f} per word",
            f"Sample citations: {citations_found[:3] if citations_found else 'None'}"
        ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.9,
            suggestions=suggestions
        )


# Additional domain-specific advanced rules

class CategoryBasedRule(AdvancedRule):
    """Base class for rules that evaluate text based on categorized term matching."""
    
    def __init__(self, rule_type: str, weight: float, params: Dict[str, Any]):
        super().__init__(rule_type, weight, params)
        self.categories = self.get_categories()
        self.scoring_weights = self.get_scoring_weights()
        self.thresholds = self.get_thresholds()
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Override in subclasses to define category terms."""
        raise NotImplementedError
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Override in subclasses to define scoring weights."""
        return {"category_coverage": 0.7, "term_density": 0.3, "density_multiplier": 10}
    
    def get_thresholds(self) -> Dict[str, float]:
        """Override in subclasses to define score thresholds."""
        return {"high": 0.7, "medium": 0.4}
    
    def get_feedback_messages(self, score: float) -> Tuple[str, List[str]]:
        """Override in subclasses to provide domain-specific feedback.
        
        Args:
            score: The calculated score (0.0-1.0)
            
        Returns:
            Tuple of (reasoning_message, list_of_suggestions)
        """
        raise NotImplementedError
    
    @lru_cache(maxsize=128)
    def _find_terms_in_text(self, text_lower: str, terms_tuple: Tuple[str, ...]) -> Tuple[str, ...]:
        """Cached method to find terms in text."""
        return tuple(term for term in terms_tuple if term in text_lower)
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        text_lower = text.lower()
        found_categories = {}
        total_found = 0
        
        for category, terms in self.categories.items():
            # Use cached method for better performance
            found_terms = self._find_terms_in_text(text_lower, tuple(terms))
            found_categories[category] = list(found_terms)
            total_found += len(found_terms)
        
        # Calculate score components
        category_coverage = len([cat for cat, terms in found_categories.items() if terms]) / len(self.categories)
        term_density = total_found / len(text.split()) if text.split() else 0
        
        weights = self.scoring_weights
        score = min(1.0, (
            category_coverage * weights["category_coverage"] + 
            term_density * weights["density_multiplier"] * weights["term_density"]
        ))
        
        # Build evidence
        evidence = [
            f"Categories covered: {len([cat for cat, terms in found_categories.items() if terms])}/{len(self.categories)}",
            f"Terms found: {total_found}",
            f"Term density: {term_density:.4f}"
        ]
        
        for category, terms in found_categories.items():
            if terms:
                evidence.append(f"{category.title()}: {', '.join(terms[:3])}")
        
        reasoning, suggestions = self.get_feedback_messages(score)
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.85,
            suggestions=suggestions
        )


class SecurityAssessmentRule(CategoryBasedRule):
    """Evaluates security awareness and best practices in text."""
    
    def get_categories(self) -> Dict[str, List[str]]:
        return {
            'vulnerabilities': ['injection', 'xss', 'csrf', 'sql injection', 'buffer overflow', 'authentication', 'authorization'],
            'best_practices': ['validation', 'sanitization', 'encryption', 'hashing', 'secure', 'https', 'ssl', 'tls'],
            'security_tools': ['firewall', 'antivirus', 'penetration test', 'vulnerability scan', 'security audit'],
            'compliance': ['gdpr', 'hipaa', 'pci dss', 'sox', 'compliance', 'privacy', 'data protection']
        }
    
    def get_feedback_messages(self, score: float) -> Tuple[str, List[str]]:
        if score >= self.thresholds["high"]:
            return ("Text demonstrates strong security awareness and best practices", [])
        elif score >= self.thresholds["medium"]:
            return ("Text shows moderate security awareness with room for improvement", [
                "Include more security vulnerability discussions",
                "Add specific security best practices",
                "Reference security tools and compliance standards"
            ])
        else:
            return ("Text lacks security awareness and best practices", [
                "Add discussion of common security vulnerabilities",
                "Include security best practices and mitigation strategies",
                "Reference relevant compliance requirements",
                "Mention security tools and assessment methods"
            ])
        
        evidence = [
            f"Security categories covered: {len([cat for cat, terms in found_categories.items() if terms])}/{len(security_indicators)}",
            f"Security terms found: {total_found}",
            f"Term density: {term_density:.4f}"
        ]
        
        for category, terms in found_categories.items():
            if terms:
                evidence.append(f"{category.title()}: {', '.join(terms[:3])}")
        
        if score >= 0.7:
            reasoning = "Text demonstrates strong security awareness and best practices"
            suggestions = []
        elif score >= 0.4:
            reasoning = "Text shows moderate security awareness with room for improvement"
            suggestions = [
                "Include more security vulnerability discussions",
                "Add specific security best practices",
                "Reference security tools and compliance standards"
            ]
        else:
            reasoning = "Text lacks security awareness and best practices"
            suggestions = [
                "Add discussion of common security vulnerabilities",
                "Include security best practices and mitigation strategies",
                "Reference relevant compliance requirements",
                "Mention security tools and assessment methods"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.85,
            suggestions=suggestions
        )


class LegalComplianceRule(AdvancedRule):
    """Evaluates legal compliance and risk awareness in text."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        jurisdiction = self.params.get('jurisdiction', 'general')
        compliance_areas = self.params.get('compliance_areas', [
            'data privacy', 'employment law', 'contract law', 'intellectual property',
            'regulatory compliance', 'liability', 'terms of service', 'privacy policy'
        ])
        
        legal_indicators = {
            'risk_awareness': ['risk', 'liability', 'compliance', 'legal', 'regulation', 'statute', 'law'],
            'documentation': ['contract', 'agreement', 'terms', 'policy', 'disclosure', 'notice'],
            'protection': ['indemnification', 'limitation of liability', 'disclaimer', 'warranty'],
            'process': ['review', 'approval', 'audit', 'assessment', 'due diligence']
        }
        
        text_lower = text.lower()
        found_indicators = {}
        compliance_mentions = 0
        
        for category, terms in legal_indicators.items():
            found_terms = [term for term in terms if term in text_lower]
            found_indicators[category] = found_terms
        
        for area in compliance_areas:
            if area.lower() in text_lower:
                compliance_mentions += 1
        
        # Score based on legal awareness and compliance coverage
        indicator_score = len([cat for cat, terms in found_indicators.items() if terms]) / len(legal_indicators)
        compliance_score = compliance_mentions / len(compliance_areas) if compliance_areas else 0
        
        score = min(1.0, (indicator_score * 0.6 + compliance_score * 0.4))
        
        evidence = [
            f"Legal indicator categories: {len([cat for cat, terms in found_indicators.items() if terms])}/{len(legal_indicators)}",
            f"Compliance areas mentioned: {compliance_mentions}/{len(compliance_areas)}",
            f"Jurisdiction: {jurisdiction}"
        ]
        
        if score >= 0.7:
            reasoning = f"Text demonstrates strong legal compliance awareness for {jurisdiction} jurisdiction"
            suggestions = []
        elif score >= 0.4:
            reasoning = f"Text shows moderate legal awareness with compliance gaps for {jurisdiction}"
            suggestions = [
                "Add more specific legal risk discussions",
                "Include relevant compliance requirements",
                "Reference applicable laws and regulations"
            ]
        else:
            reasoning = f"Text lacks adequate legal compliance awareness for {jurisdiction}"
            suggestions = [
                "Consult legal counsel for compliance requirements",
                "Add risk assessment and mitigation strategies",
                "Include necessary legal disclaimers and notices",
                "Reference relevant laws and regulatory frameworks"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.8,
            suggestions=suggestions
        )


class MedicalAccuracyRule(AdvancedRule):
    """Evaluates medical accuracy and appropriate clinical language."""
    
    def get_default_medical_terms(self) -> List[str]:
        """Get default medical terminology list."""
        return [
            'diagnosis', 'treatment', 'symptoms', 'patient', 'clinical', 'therapeutic',
            'medication', 'dosage', 'contraindication', 'side effects', 'prognosis'
        ]
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        medical_terminology = self.params.get('medical_terms', self.get_default_medical_terms())
        
        accuracy_indicators = {
            'precision': ['specific', 'precise', 'exact', 'measured', 'documented'],
            'caution': ['may', 'might', 'could', 'potential', 'possible', 'consult', 'physician'],
            'evidence': ['study', 'research', 'clinical trial', 'evidence', 'data', 'statistics'],
            'disclaimers': ['not medical advice', 'consult doctor', 'healthcare provider', 'medical professional']
        }
        
        text_lower = text.lower()
        medical_term_count = sum(1 for term in medical_terminology if term.lower() in text_lower)
        
        found_indicators = {}
        for category, terms in accuracy_indicators.items():
            found_terms = [term for term in terms if term in text_lower]
            found_indicators[category] = found_terms
        
        # Score based on medical terminology use and accuracy indicators
        terminology_score = self._calculate_terminology_score(medical_term_count, len(medical_terminology))
        accuracy_score = self._calculate_accuracy_score(found_indicators, accuracy_indicators)
        
        score = min(1.0, (terminology_score * 0.4 + accuracy_score * 0.6))
        
        evidence = self._build_medical_evidence(medical_term_count, medical_terminology, found_indicators, accuracy_indicators)
        reasoning, suggestions = self._get_medical_feedback(score)
    
    def _calculate_terminology_score(self, term_count: int, total_terms: int) -> float:
        """Calculate score based on medical terminology usage."""
        return min(1.0, term_count / max(1, total_terms * MEDICAL_TERMINOLOGY_THRESHOLD))
    
    def _calculate_accuracy_score(self, found_indicators: Dict, accuracy_indicators: Dict) -> float:
        """Calculate score based on accuracy indicators."""
        return len([cat for cat, terms in found_indicators.items() if terms]) / len(accuracy_indicators)
    
    def _build_medical_evidence(self, term_count: int, total_terms: int, found_indicators: Dict, accuracy_indicators: Dict) -> List[str]:
        """Build evidence list for medical accuracy evaluation."""
        evidence = [
            f"Medical terms used: {term_count}/{total_terms}",
            f"Accuracy indicators: {len([cat for cat, terms in found_indicators.items() if terms])}/{len(accuracy_indicators)}"
        ]
        
        for category, terms in found_indicators.items():
            if terms:
                evidence.append(f"{category.title()}: {', '.join(terms[:3])}")
        
        return evidence
    
    def _get_medical_feedback(self, score: float) -> Tuple[str, List[str]]:
        """Get reasoning and suggestions based on medical accuracy score."""
        if score >= 0.8:
            return ("Text demonstrates appropriate medical accuracy and professional language", [])
        elif score >= 0.5:
            return ("Text shows moderate medical accuracy with room for improvement", [
                "Add more specific medical terminology where appropriate",
                "Include appropriate medical disclaimers",
                "Reference clinical evidence or studies",
                "Use more cautious language for medical claims"
            ])
        else:
            return ("Text lacks appropriate medical accuracy and professional standards", [
                "Consult medical professionals for accuracy review",
                "Add required medical disclaimers",
                "Use evidence-based medical information",
                "Avoid definitive medical claims without proper qualification"
            ])
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.9,
            suggestions=suggestions
        )


class FinancialComplianceRule(AdvancedRule):
    """Evaluates financial advice compliance and risk disclosures."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        financial_terms = [
            'investment', 'portfolio', 'risk', 'return', 'diversification', 'asset allocation',
            'market volatility', 'financial advisor', 'securities', 'bonds', 'stocks', 'mutual funds'
        ]
        
        compliance_indicators = {
            'disclaimers': ['not financial advice', 'consult advisor', 'past performance', 'no guarantee'],
            'risk_disclosure': ['risk', 'loss', 'volatility', 'market risk', 'investment risk'],
            'qualifications': ['may', 'might', 'could', 'potential', 'consider', 'evaluate'],
            'professional_reference': ['financial advisor', 'certified', 'licensed', 'qualified professional']
        }
        
        text_lower = text.lower()
        financial_term_count = sum(1 for term in financial_terms if term.lower() in text_lower)
        
        found_indicators = {}
        for category, terms in compliance_indicators.items():
            found_terms = [term for term in terms if term in text_lower]
            found_indicators[category] = found_terms
        
        # Higher compliance requirements for financial content
        terminology_score = min(1.0, financial_term_count / max(1, len(financial_terms) * 0.2))
        compliance_score = len([cat for cat, terms in found_indicators.items() if terms]) / len(compliance_indicators)
        
        # Financial content requires strong compliance
        score = min(1.0, (terminology_score * 0.3 + compliance_score * 0.7))
        
        evidence = [
            f"Financial terms used: {financial_term_count}/{len(financial_terms)}",
            f"Compliance indicators: {len([cat for cat, terms in found_indicators.items() if terms])}/{len(compliance_indicators)}"
        ]
        
        if score >= 0.8:
            reasoning = "Text demonstrates strong financial compliance and appropriate risk disclosures"
            suggestions = []
        elif score >= 0.5:
            reasoning = "Text shows moderate financial compliance with missing risk disclosures"
            suggestions = [
                "Add required financial disclaimers",
                "Include appropriate risk disclosures",
                "Reference qualified financial professionals",
                "Use more cautious language for financial recommendations"
            ]
        else:
            reasoning = "Text lacks adequate financial compliance and risk disclosures"
            suggestions = [
                "Add 'not financial advice' disclaimer",
                "Include comprehensive risk warnings",
                "Reference past performance disclaimers",
                "Recommend consultation with qualified financial advisors",
                "Avoid definitive financial predictions"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.95,
            suggestions=suggestions
        )


class AccessibilityRule(AdvancedRule):
    """Evaluates content accessibility and inclusive language."""
    
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        accessibility_indicators = {
            'inclusive_language': ['accessible', 'inclusive', 'diverse', 'everyone', 'all users'],
            'clear_structure': ['heading', 'section', 'list', 'step', 'first', 'next', 'finally'],
            'descriptive': ['describe', 'explain', 'detail', 'specific', 'clear', 'example'],
            'alternative_formats': ['alt text', 'caption', 'transcript', 'audio', 'visual', 'screen reader']
        }
        
        problematic_language = [
            'click here', 'see below', 'look at', 'as you can see', 'obviously', 'simply', 'just', 'easy'
        ]
        
        text_lower = text.lower()
        
        found_indicators = {}
        for category, terms in accessibility_indicators.items():
            found_terms = [term for term in terms if term in text_lower]
            found_indicators[category] = found_terms
        
        problematic_count = sum(1 for phrase in problematic_language if phrase in text_lower)
        
        # Score based on accessibility indicators and absence of problematic language
        positive_score = len([cat for cat, terms in found_indicators.items() if terms]) / len(accessibility_indicators)
        penalty = min(0.5, problematic_count * 0.1)  # Penalty for problematic language
        
        score = max(0.0, positive_score - penalty)
        
        evidence = [
            f"Accessibility indicators: {len([cat for cat, terms in found_indicators.items() if terms])}/{len(accessibility_indicators)}",
            f"Problematic phrases found: {problematic_count}"
        ]
        
        if score >= 0.8:
            reasoning = "Text demonstrates strong accessibility awareness and inclusive design"
            suggestions = []
        elif score >= 0.5:
            reasoning = "Text shows moderate accessibility awareness with room for improvement"
            suggestions = [
                "Use more descriptive link text instead of 'click here'",
                "Add clear headings and structure",
                "Include alternative format considerations",
                "Use more inclusive language"
            ]
        else:
            reasoning = "Text lacks accessibility awareness and inclusive design principles"
            suggestions = [
                "Replace vague references with specific descriptions",
                "Add clear structural elements (headings, lists)",
                "Consider users with different abilities",
                "Provide alternative format information",
                "Use inclusive and accessible language patterns"
            ]
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning=reasoning,
            evidence=evidence,
            confidence=0.85,
            suggestions=suggestions
        )


# Registry of advanced rule types
ADVANCED_RULE_TYPES = {
    'readability': ReadabilityRule,
    'semantic_coherence': SemanticCoherenceRule,
    'argument_structure': ArgumentStructureRule,
    'domain_expertise': DomainExpertiseRule,
    'citation_quality': CitationQualityRule,
    'security_assessment': SecurityAssessmentRule,
    'legal_compliance': LegalComplianceRule,
    'medical_accuracy': MedicalAccuracyRule,
    'financial_compliance': FinancialComplianceRule,
    'accessibility': AccessibilityRule,
}


def create_advanced_rule(rule_type: str, weight: float, params: Dict[str, Any]) -> AdvancedRule:
    """Factory function to create advanced rules."""
    if rule_type not in ADVANCED_RULE_TYPES:
        available_types = ', '.join(ADVANCED_RULE_TYPES.keys())
        raise ValueError(
            f"Unknown advanced rule type: '{rule_type}'. "
            f"Available types: {available_types}"
        )
    
    try:
        rule_class = ADVANCED_RULE_TYPES[rule_type]
        return rule_class(rule_type, weight, params)
    except Exception as e:
        raise ValueError(
            f"Failed to create rule of type '{rule_type}': {str(e)}"
        ) from e


def get_available_rule_types() -> List[str]:
    """Get list of available advanced rule types."""
    return list(ADVANCED_RULE_TYPES.keys())


def get_rule_requirements(rule_type: str) -> Dict[str, Any]:
    """Get dependency requirements for a specific rule type."""
    requirements = {
        'readability': {'packages': ['textstat'], 'available': TEXTSTAT_AVAILABLE},
        'semantic_coherence': {'packages': ['spacy', 'sklearn'], 'available': SPACY_AVAILABLE and SKLEARN_AVAILABLE},
        'argument_structure': {'packages': [], 'available': True},
        'domain_expertise': {'packages': [], 'available': True},
        'citation_quality': {'packages': [], 'available': True},
    }
    
    return requirements.get(rule_type, {'packages': [], 'available': False})