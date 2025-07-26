# ClarityAI API Documentation

## Overview

ClarityAI provides both programmatic APIs and command-line interfaces for integrating AI evaluation and training into your applications.

---

## Python API

### Core Classes

#### `Template`

The main class for creating and managing evaluation templates.

```python
from clarity.scorer import Template

# Create a new template
template = Template(name="my_template")
template.description = "Evaluates text quality"

# Add rules
template.add_rule("contains_phrase", weight=2.0, phrase="helpful")
template.add_rule("word_count", weight=1.0, min_words=10, max_words=100)
template.add_rule("sentiment_positive", weight=1.5)

# Evaluate text
score = template.evaluate("This is a helpful guide with examples.")
detailed_result = template.evaluate_detailed("This is a helpful guide.")
```

**Methods:**

- `add_rule(rule_type: str, weight: float, **params)` - Add a scoring rule
- `evaluate(text: str) -> float` - Get overall score (0.0-1.0)
- `evaluate_detailed(text: str) -> Dict` - Get detailed breakdown
- `evaluate_with_explanations(text: str) -> Dict` - Get rich explanations
- `to_yaml(path: str)` - Save template to YAML file
- `from_yaml(path: str)` - Load template from YAML file

#### `Rule`

Individual scoring rules with specific evaluation logic.

```python
from clarity.scorer import Rule

rule = Rule(
    rule_type="contains_phrase",
    weight=2.0,
    params={"phrase": "example"}
)

score = rule.evaluate("This text contains an example.")
```

### Advanced Rules

```python
from clarity.advanced_rules import create_advanced_rule

# Create domain-specific rule
security_rule = create_advanced_rule(
    "security_assessment",
    weight=3.0,
    params={}
)

# Evaluate with rich explanations
explanation = security_rule.evaluate_with_explanation(text)
print(explanation.reasoning)
print(explanation.suggestions)
```

### Utility Functions

#### `score(text, template)`

Quick scoring function for simple use cases.

```python
from clarity.scorer import score

result = score("Your text here", "path/to/template.yaml")
```

#### `score_detailed(text, template)`

Detailed scoring with rule breakdown.

```python
from clarity.scorer import score_detailed

result = score_detailed("Your text here", "path/to/template.yaml")
print(result['total_score'])
for rule in result['rule_scores']:
    print(f"{rule['rule_type']}: {rule['raw_score']}")
```

---

## Command Line Interface

### Basic Commands

#### Score Text

```bash
# Score a text file
clarity score document.txt --template template.yaml

# Score direct text input
clarity score --text "Your text here" --template template.yaml

# Get detailed breakdown
clarity score document.txt --template template.yaml --detailed
```

#### Create Templates

```bash
# Create new template
clarity create-template --name "my-template" --output my-template.yaml

# With description
clarity create-template --name "code-review" \
                       --description "Evaluates code review quality" \
                       --output templates/code-review.yaml
```

#### Train Models

```bash
# Basic training
clarity train --model microsoft/DialoGPT-small \
              --template template.yaml \
              --steps 50

# Advanced training options
clarity train --model microsoft/DialoGPT-medium \
              --template template.yaml \
              --steps 100 \
              --learning-rate 1e-5 \
              --batch-size 16 \
              --output models/my-model
```

#### Demo Mode

```bash
# Run interactive demo
clarity demo --model microsoft/DialoGPT-small

# With custom template
clarity demo --model gpt2 --template my-template.yaml
```

### Command Options

#### Global Options

- `--help` - Show help message
- `--version` - Show version information
- `--verbose` - Enable verbose output
- `--quiet` - Suppress non-error output

#### Score Command Options

- `--template PATH` - Path to YAML template file (required)
- `--text TEXT` - Direct text input (alternative to file)
- `--detailed` - Show detailed rule breakdown
- `--output FORMAT` - Output format (text, json, yaml)

#### Train Command Options

- `--model NAME` - HuggingFace model name
- `--template PATH` - Path to template file
- `--steps INT` - Number of training steps (default: 20)
- `--learning-rate FLOAT` - Learning rate (default: 1.41e-5)
- `--batch-size INT` - Batch size (default: 16)
- `--output PATH` - Output directory (default: runs/)

---

## REST API (Future)

### Endpoints

#### POST /api/v1/score

Score text against a template.

```json
{
  "text": "Text to evaluate",
  "template": "template_name_or_yaml",
  "detailed": true
}
```

Response:
```json
{
  "score": 0.85,
  "breakdown": [
    {
      "rule_type": "contains_phrase",
      "score": 1.0,
      "weight": 2.0
    }
  ]
}
```

#### POST /api/v1/train

Start model training.

```json
{
  "model": "microsoft/DialoGPT-small",
  "template": "template_name",
  "steps": 50,
  "learning_rate": 1e-5
}
```

---

## Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
from clarity.scorer import Template

app = Flask(__name__)
template = Template.from_yaml("my-template.yaml")

@app.route('/score', methods=['POST'])
def score_text():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = template.evaluate_detailed(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Batch Processing

```python
import pandas as pd
from clarity.scorer import Template

# Load template
template = Template.from_yaml("quality-check.yaml")

# Process CSV file
df = pd.read_csv("texts.csv")
df['quality_score'] = df['text'].apply(template.evaluate)

# Save results
df.to_csv("scored_texts.csv", index=False)
```

### Custom Rule Development

```python
from clarity.advanced_rules import AdvancedRule, RuleExplanation

class CustomRule(AdvancedRule):
    def evaluate_with_explanation(self, text: str) -> RuleExplanation:
        # Your custom logic here
        score = self.custom_scoring_logic(text)
        
        return RuleExplanation(
            rule_type=self.rule_type,
            score=score,
            reasoning="Custom rule evaluation",
            evidence=["Evidence item 1", "Evidence item 2"],
            confidence=0.9,
            suggestions=["Suggestion 1", "Suggestion 2"]
        )
    
    def custom_scoring_logic(self, text: str) -> float:
        # Implement your scoring algorithm
        return 0.8

# Register custom rule
from clarity.advanced_rules import ADVANCED_RULE_TYPES
ADVANCED_RULE_TYPES['custom_rule'] = CustomRule
```

---

## Error Handling

### Common Exceptions

- `FileNotFoundError` - Template file not found
- `ValueError` - Invalid rule type or parameters
- `yaml.YAMLError` - Invalid YAML syntax in template
- `ImportError` - Missing optional dependencies for advanced rules

### Error Response Format

```python
{
    "error": "Error description",
    "error_type": "ValueError",
    "details": {
        "rule_type": "invalid_rule",
        "line": 15
    }
}
```

---

## Performance Considerations

### Optimization Tips

1. **Template Caching**: Load templates once and reuse
2. **Batch Processing**: Process multiple texts in batches
3. **Rule Selection**: Use only necessary rules for better performance
4. **Advanced Rules**: Some advanced rules require additional dependencies

### Benchmarks

- Basic rules: ~1ms per evaluation
- Advanced rules: ~10-50ms per evaluation
- Training: Depends on model size and steps

---

## Configuration

### Environment Variables

- `CLARITY_CACHE_DIR` - Cache directory for models and data
- `CLARITY_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `CLARITY_MAX_WORKERS` - Maximum worker threads for parallel processing

### Configuration File

Create `~/.clarity/config.yaml`:

```yaml
cache_dir: ~/.clarity/cache
log_level: INFO
default_model: microsoft/DialoGPT-small
max_workers: 4

templates:
  default_path: ./templates
  auto_reload: true

training:
  default_steps: 20
  default_batch_size: 16
  checkpoint_interval: 10
```

---

## Support

### Getting Help

- **Documentation**: [docs/README.md](README.md)
- **Troubleshooting**: [docs/troubleshooting-guide.md](troubleshooting-guide.md)
- **Examples**: [docs/use-cases/](use-cases/)
- **GitHub Issues**: Report bugs and request features

### Version Compatibility

- Python: 3.9+
- PyTorch: 1.9.0+
- Transformers: 4.20.0+
- Streamlit: 1.20.0+

---

**Ready to integrate ClarityAI into your application? Start with the examples above and refer to our comprehensive documentation for advanced use cases.**