# ClarityAI Quick Reference

> **Instant Access**: Keep this page bookmarked for quick command and syntax reference.

## 🚀 Essential Commands

### Installation & Setup
```bash
# Install ClarityAI
pip install -e .

# Verify installation
clarity --help

# Start web interface
streamlit run app.py
```

### Basic Scoring
```bash
# Score a text file
clarity score my-text.txt --template my-template.yaml

# Score with detailed breakdown
clarity score my-text.txt --template my-template.yaml --detailed

# Score direct text input
clarity score --text "Your text here" --template my-template.yaml
```

### Template Management
```bash
# Create new template
clarity create-template --name "my-template" --output my-template.yaml

# Test template with demo
clarity demo --model microsoft/DialoGPT-small
```

### Training
```bash
# Basic training
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20

# Training with custom settings
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 50 --batch-size 8 --learning-rate 1e-5
```

---

## 📝 Template Syntax

### Basic Template Structure
```yaml
name: template_name
description: What this template does

rules:
  - type: rule_type
    weight: 1.0
    params:
      parameter: value
```

### Rule Types Quick Reference

#### 1. Check for Specific Phrase
```yaml
- type: contains_phrase
  weight: 2.0
  params:
    phrase: "helpful"
```

#### 2. Validate Text Length
```yaml
- type: word_count
  weight: 1.0
  params:
    min_words: 10
    max_words: 50
```

#### 3. Detect Positive Language
```yaml
- type: sentiment_positive
  weight: 1.5
  params: {}
```

#### 4. Pattern Matching
```yaml
- type: regex_match
  weight: 1.0
  params:
    pattern: "[A-Z][a-z]+"
```

#### 5. Similarity to Target Text
```yaml
- type: cosine_sim
  weight: 1.0
  params:
    target: "machine learning"
```

---

## 🎯 Common Template Examples

### Code Review Template
```yaml
name: code_review
description: Evaluates code review comments

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "suggestion"
  
  - type: sentiment_positive
    weight: 1.0
    params: {}
  
  - type: word_count
    weight: 1.0
    params:
      min_words: 10
      max_words: 200
```

### Educational Content Template
```yaml
name: educational_content
description: Evaluates learning materials

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "example"
  
  - type: contains_phrase
    weight: 1.5
    params:
      phrase: "step"
  
  - type: word_count
    weight: 1.0
    params:
      min_words: 50
      max_words: 500
  
  - type: sentiment_positive
    weight: 1.0
    params: {}
```

### Customer Support Template
```yaml
name: customer_support
description: Evaluates customer service responses

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "help"
  
  - type: contains_phrase
    weight: 1.5
    params:
      phrase: "understand"
  
  - type: sentiment_positive
    weight: 2.0
    params: {}
  
  - type: word_count
    weight: 1.0
    params:
      min_words: 20
      max_words: 150
```

---

## 🔍 Troubleshooting Quick Fixes

### Installation Issues
```bash
# Update pip first
pip install --upgrade pip

# Try user install
pip install -e . --user

# Use virtual environment
python -m venv clarity-env
source clarity-env/bin/activate  # Mac/Linux
clarity-env\Scripts\activate     # Windows
pip install -e .
```

### Command Not Found
```bash
# Try as Python module
python -m clarity.cli --help

# Check installation
pip show clarity-ai

# Reinstall
pip uninstall clarity-ai
pip install -e .
```

### Template Errors
```bash
# Test with demo template first
clarity score test.txt --template templates/demo.yaml

# Validate YAML syntax online
# Go to: yamllint.com

# Check file exists
ls -la your-template.yaml
```

### Web Interface Issues
```bash
# Install streamlit
pip install streamlit

# Try different port
streamlit run app.py --server.port 8502

# Clear browser cache and retry
```

---

## 📊 Understanding Scores

### Score Interpretation
- **0.0**: Text completely fails template criteria
- **0.1-0.3**: Poor match to template
- **0.4-0.6**: Moderate match to template  
- **0.7-0.9**: Good match to template
- **1.0**: Perfect match to template

### Score Calculation
```
Final Score = Total Weighted Score ÷ Total Weight

Example:
Rule 1: Raw Score 1.0 × Weight 2.0 = 2.0
Rule 2: Raw Score 0.5 × Weight 1.0 = 0.5
Rule 3: Raw Score 0.8 × Weight 1.5 = 1.2

Total Weighted Score: 2.0 + 0.5 + 1.2 = 3.7
Total Weight: 2.0 + 1.0 + 1.5 = 4.5
Final Score: 3.7 ÷ 4.5 = 0.822
```

---

## 🗂️ File Organization

### Recommended Structure
```
your-project/
├── templates/
│   ├── my-template.yaml
│   └── backup-template.yaml
├── test-texts/
│   ├── sample1.txt
│   └── sample2.txt
├── results/
│   └── training-logs/
└── scripts/
    └── batch-score.sh
```

### File Naming Conventions
- Templates: `descriptive-name.yaml`
- Text files: `test-description.txt`
- Avoid spaces in filenames
- Use lowercase with hyphens

---

## 🎨 Web Interface Quick Guide

### Left Panel (Template Editor)
1. **Template Management**: Choose template source
2. **Template Editor**: Edit YAML directly
3. **Template Info**: View template details
4. **Download**: Save your template

### Right Panel (Live Scoring)
1. **Text Input**: Enter or select text
2. **Score Text**: Run evaluation
3. **Results**: View scores and breakdown
4. **History**: Track score changes
5. **Batch Scoring**: Test multiple texts

### Sidebar (Help)
- Rule type examples
- Quick start guide
- About ClarityAI

---

## 🔗 Quick Links

### Documentation
- [Complete Guide](README.md) - Full documentation
- [Step-by-Step Tutorial](step-by-step-tutorial.md) - Hands-on learning
- [Visual Guide](visual-guide.md) - Diagrams and flowcharts
- [Troubleshooting](troubleshooting-guide.md) - Problem solutions

### Online Resources
- [YAML Validator](https://yamllint.com) - Check template syntax
- [Regex Tester](https://regex101.com) - Test regex patterns
- [Python.org](https://python.org) - Download Python

---

## 📱 Mobile-Friendly Commands

### One-Line Test Commands
```bash
# Quick test
clarity score --text "test" --template templates/demo.yaml

# Quick detailed test  
clarity score --text "helpful example" --template templates/demo.yaml --detailed

# Quick web start
streamlit run app.py
```

### Emergency Reset
```bash
# Complete reset sequence
pip uninstall clarity-ai && pip install -e . && clarity --help
```

---

**💡 Pro Tip**: Bookmark this page in your browser for instant access to commands and syntax while working with ClarityAI.