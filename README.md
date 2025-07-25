# ClarityAI

> **Train LLMs with teacher-style rubrics**

ClarityAI lets you train AI language models the way a teacher grades students: build a scoring rubric, test it on sample text, then use it to improve AI models.

## 🎯 What is ClarityAI?

ClarityAI is a tool that helps you:
- **Create scoring templates** with custom rules (like "contains helpful words" or "has 10-50 words")
- **Test your templates** on sample text to see how they work
- **Train AI models** to write better text using your scoring criteria
- **Track progress** and see improvements over time

## 🚀 Quick Start (5 Minutes)

### Step 1: Install ClarityAI
```bash
pip install -e .
```

### Step 2: Test with Sample Template
```bash
clarity score --text "This is a helpful guide with clear examples" --template templates/demo.yaml --detailed
```

### Step 3: Start Web Interface
```bash
streamlit run app.py
```
Then open your browser to `http://localhost:8501`

## 📚 Complete Documentation

**Choose your learning style:**

- 📖 **[Complete Documentation](docs/README.md)** - Comprehensive guide with step-by-step instructions
- 🎨 **[Visual Guide](docs/visual-guide.md)** - Diagrams, flowcharts, and visual explanations  
- 👨‍🏫 **[Step-by-Step Tutorial](docs/step-by-step-tutorial.md)** - Hands-on tutorial with verification steps

## 🔧 Installation

**Prerequisites:**
- Python 3.9 or newer
- 2 GB free disk space
- Internet connection

**Install:**
```bash
cd /path/to/clarity-ai
pip install -e .
```

**Verify:**
```bash
clarity --help
```

## 💻 Usage Examples

### Command Line Interface

**Score text with detailed breakdown:**
```bash
clarity score my-text.txt --template my-template.yaml --detailed
```

**Score text directly:**
```bash
clarity score --text "Your text here" --template my-template.yaml
```

**Create a new template:**
```bash
clarity create-template --name "my-template" --output my-template.yaml
```

**Train an AI model:**
```bash
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20
```

### Web Interface

Start the visual interface:
```bash
streamlit run app.py
```

Features:
- Visual template editor
- Live text scoring
- Rule breakdown display
- Score history tracking
- Batch text processing

## 📝 Creating Templates

Templates define how ClarityAI scores text. Here's a simple example:

```yaml
name: helpful_content
description: Scores text based on helpfulness and clarity

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "helpful"

  - type: word_count
    weight: 1.0
    params:
      min_words: 10
      max_words: 50

  - type: sentiment_positive
    weight: 1.5
    params: {}
```

**Available Rule Types:**
- `contains_phrase` - Check for specific words/phrases
- `word_count` - Validate text length
- `sentiment_positive` - Detect positive language
- `regex_match` - Pattern matching
- `cosine_sim` - Similarity to target text

## 🤖 Training Models

Use your templates to train AI models:

```bash
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20
```

**What happens:**
1. Model generates sample text
2. Your template scores each sample
3. Model learns from high-scoring examples
4. Process repeats to improve performance

## 📊 Project Status

**Current Version:** 0.1.0 (Under Development)

**Completed Features:**
- ✅ Rubric-based scoring engine
- ✅ Command line interface
- ✅ Streamlit web interface
- ✅ PPO training loop
- ✅ Run tracking and logging
- ✅ Multiple rule types
- ✅ Template system

**In Development:**
- 🔄 Additional rule types
- 🔄 Advanced training options
- 🔄 Model comparison tools

## 🔍 Troubleshooting

**Installation Issues:**
```bash
# Update pip first
pip install --upgrade pip

# Try user install
pip install -e . --user
```

**Command Not Found:**
```bash
# Check installation
python -m clarity.cli --help
```

**Template Errors:**
- Check YAML syntax (spaces, not tabs)
- Verify all required fields are present
- Use online YAML validator

## 📞 Getting Help

1. **Read the Documentation**: Start with [docs/README.md](docs/README.md)
2. **Try the Tutorial**: Follow [docs/step-by-step-tutorial.md](docs/step-by-step-tutorial.md)
3. **Check Troubleshooting**: See the troubleshooting sections in documentation
4. **Use Visual Guide**: Reference [docs/visual-guide.md](docs/visual-guide.md) for diagrams

## 🏗️ Project Structure

```
clarity-ai/
├── clarity/           # Main package
│   ├── cli.py        # Command line interface
│   ├── scorer.py     # Scoring engine
│   └── trainer.py    # Training system
├── templates/        # Example templates
├── tests/           # Test suite
├── docs/            # Complete documentation
├── app.py           # Web interface
└── setup.py         # Installation config
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

ClarityAI is under active development. The codebase includes comprehensive tests and documentation to support contributors.

---

**Ready to get started?** Begin with the [Complete Documentation](docs/README.md) or jump into the [Step-by-Step Tutorial](docs/step-by-step-tutorial.md).