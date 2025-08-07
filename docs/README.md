    q# ClarityAI Complete Documentation

> **IMPORTANT**: This documentation is designed with clear, step-by-step instructions. Each section builds on the previous one. Do not skip any steps.

## 📋 Table of Contents

1. [🎯 What is ClarityAI?](#what-is-clarityai)
2. [🔧 Installation Guide](#installation-guide)
3. [🚀 Quick Start Tutorial](#quick-start-tutorial)
4. [💻 Web Interface Guide](#web-interface-guide)
5. [⌨️ Command Line Guide](#command-line-guide)
6. [📝 Creating Templates](#creating-templates)
7. [🤖 Training Models](#training-models)
8. [🔍 Troubleshooting](#troubleshooting)
9. [📞 Getting Help](#getting-help)

---

## 🎯 What is ClarityAI?

ClarityAI is a tool that helps you train AI language models using scoring rubrics, similar to how a teacher grades student work.

### Key Concepts (Read These First):

**Template**: A collection of scoring rules that define how to evaluate text
**Rule**: A single criterion for scoring (like "contains helpful words" or "has 10-50 words")
**Score**: A number between 0.0 and 1.0 that shows how well text meets your criteria
**Training**: The process of improving an AI model using your scoring template

### What You Can Do:
- ✅ Create scoring templates with custom rules
- ✅ Test your templates on sample text
- ✅ Use a visual web interface to build templates
- ✅ Train AI models to write better text
- ✅ Track training progress and results

---

## 🔧 Installation Guide

### Prerequisites Check
Before starting, verify you have:
- Python 3.9 or newer installed
- Terminal/Command Prompt access
- Internet connection for downloading packages

### Step-by-Step Installation

**Step 1: Open Terminal**
- On Mac: Press `Cmd + Space`, type "Terminal", press Enter
- On Windows: Press `Win + R`, type "cmd", press Enter
- On Linux: Press `Ctrl + Alt + T`

**Step 2: Navigate to Project Directory**
```bash
cd /path/to/clarity-ai
```
⚠️ **CRITICAL**: Replace `/path/to/clarity-ai` with the actual path to your ClarityAI folder

**Step 3: Install ClarityAI**
```bash
pip install -e .
```
⏳ **Wait**: This will take 2-5 minutes. Do not close the terminal.

**Step 4: Verify Installation**
```bash
clarity --help
```
✅ **Success Check**: You should see a help message with available commands.

❌ **If you see an error**: Go to [Troubleshooting](#troubleshooting) section.

---

## 🚀 Quick Start Tutorial

This tutorial will take you through your first ClarityAI experience step by step.

### Tutorial Overview
You will:
1. Create a simple scoring template
2. Test it on sample text
3. See detailed results

### Step 1: Create Your First Template

**1.1 Create a new file called `my-first-template.yaml`**

Copy this EXACTLY (including all spaces and dashes):

```yaml
name: my_first_template
description: A beginner template for learning ClarityAI

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

**1.2 Save the file**
- Save it in your ClarityAI project folder
- Make sure the filename ends with `.yaml`

### Step 2: Create Test Text

**2.1 Create a file called `test-text.txt`**

Copy this text:
```
This is a helpful guide that explains the basics clearly. It provides good information for beginners.
```

**2.2 Save the file**
- Save it in the same folder as your template

### Step 3: Score Your Text

**3.1 Open Terminal**
- Navigate to your ClarityAI folder (same as installation step)

**3.2 Run the scoring command**
```bash
clarity score test-text.txt --template my-first-template.yaml --detailed
```

**3.3 Read the Results**
You should see output like:
```
Overall Score: 0.750
Total Weight: 4.5

Rule Breakdown:
  ✓ contains_phrase (weight: 2.0): 1.000 → 2.000
  ✓ word_count (weight: 1.0): 1.000 → 1.000
  ✓ sentiment_positive (weight: 1.5): 0.500 → 0.750
```

### Understanding Your Results

**Overall Score**: 0.750 means your text scored 75% on your rubric
**Rule Breakdown**: Shows how each rule contributed to the final score

- `contains_phrase`: Found the word "helpful" ✅
- `word_count`: Text has 17 words (between 10-50) ✅
- `sentiment_positive`: Text has somewhat positive language ✅

---

## 💻 Web Interface Guide

The web interface provides a visual way to create templates and test scoring.

### Starting the Web Interface

**Step 1: Open Terminal**
- Navigate to your ClarityAI folder

**Step 2: Start the Web App**
```bash
streamlit run app.py
```

**Step 3: Open Your Browser**
- A browser window should open automatically
- If not, go to: `http://localhost:8501`

### Using the Web Interface

#### Left Panel: Template Editor

**Section 1: Template Management**
- Choose "Use Default Template" for your first time
- This loads a pre-made template you can modify

**Section 2: Template Editor**
- Large text box shows your template in YAML format
- Edit the text to change rules
- Green checkmark = template is valid
- Red error = template has problems

**Section 3: Template Info**
- Shows template name and description
- Lists all rules and their weights
- Use "Download Template" to save your work

#### Right Panel: Live Scoring

**Section 1: Text Input**
- Choose "Type Custom Text" to enter your own text
- Choose "Use Sample Texts" to test with examples

**Section 2: Scoring Results**
- Click "Score Text" to evaluate your text
- See overall score and rule breakdown
- View score history chart

**Section 3: Batch Scoring**
- Click "Score All Samples" to test multiple texts at once
- Compare scores across different texts

### Web Interface Workflow

1. **Start with Default Template**: Don't change anything at first
2. **Test Sample Text**: Use the sample texts to see how scoring works
3. **Modify One Rule**: Change one small thing in the template
4. **Test Again**: See how your change affected the scores
5. **Save Your Work**: Download your template when satisfied

---

## ⌨️ Command Line Guide

The command line interface provides powerful tools for advanced users.

### Available Commands

#### `clarity score` - Score text against a template

**Basic Usage:**
```bash
clarity score text-file.txt --template template.yaml
```

**With detailed breakdown:**
```bash
clarity score text-file.txt --template template.yaml --detailed
```

**Score direct text:**
```bash
clarity score --text "Your text here" --template template.yaml
```

#### `clarity demo` - Test with AI models

**Basic demo:**
```bash
clarity demo --model microsoft/DialoGPT-small
```

#### `clarity create-template` - Create new templates

**Create template:**
```bash
clarity create-template --name "my-template" --output templates/my-template.yaml
```

#### `clarity train` - Train AI models

**Basic training:**
```bash
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20
```

### Command Line Workflow

1. **Create Template**: Use `create-template` or copy from examples
2. **Test Template**: Use `score` command with sample text
3. **Refine Template**: Edit the YAML file and test again
4. **Run Demo**: Use `demo` to see AI model responses
5. **Train Model**: Use `train` when template is ready

---

## 📝 Creating Templates

Templates define how ClarityAI scores text. This section explains each rule type.

### Template Structure

Every template has this structure:
```yaml
name: template_name
description: What this template does

rules:
  - type: rule_type_1
    weight: 1.0
    params:
      parameter1: value1
      parameter2: value2
  
  - type: rule_type_2
    weight: 2.0
    params:
      parameter3: value3
```

### Rule Types Explained

#### 1. `contains_phrase` - Check for specific words/phrases

**What it does**: Gives points if text contains a specific phrase

**Example**:
```yaml
- type: contains_phrase
  weight: 2.0
  params:
    phrase: "helpful"
```

**Parameters**:
- `phrase`: The exact phrase to look for (case-insensitive)

**Scoring**: 1.0 if phrase found, 0.0 if not found

#### 2. `word_count` - Check text length

**What it does**: Gives points if text has the right number of words

**Example**:
```yaml
- type: word_count
  weight: 1.0
  params:
    min_words: 10
    max_words: 50
```

**Parameters**:
- `min_words`: Minimum number of words required
- `max_words`: Maximum number of words allowed

**Scoring**: 1.0 if within range, 0.0 if outside range

#### 3. `sentiment_positive` - Check for positive language

**What it does**: Gives points for positive, upbeat language

**Example**:
```yaml
- type: sentiment_positive
  weight: 1.5



  
  params: {}
```

**Parameters**: None (use empty `{}`)





**Scoring**: 0.0 to 1.0 based on how positive the text sounds

#### 4. `regex_match` - Pattern matching

**What it does**: Gives points if text matches a pattern

**Example**:
```yaml
- type: regex_match
  weight: 1.0
  params:
    pattern: "[A-Z][a-z]+"
```

**Parameters**:
- `pattern`: Regular expression pattern to match

**Scoring**: 1.0 if pattern found, 0.0 if not found

#### 5. `cosine_sim` - Similarity to target text

**What it does**: Gives points based on similarity to target text

**Example**:
```yaml
- type: cosine_sim
  weight: 1.0
  params:
    target: "machine learning"
```

**Parameters**:
- `target`: Text to compare against

**Scoring**: 0.0 to 1.0 based on word overlap similarity

### Template Design Tips

1. **Start Simple**: Begin with 2-3 rules
2. **Test Frequently**: Score sample text after each change
3. **Balance Weights**: Important rules should have higher weights
4. **Use Descriptive Names**: Make template names clear and specific
5. **Document Your Intent**: Use clear descriptions

### Common Template Patterns

#### Code Review Template
```yaml
name: code_review
description: Evaluates code review comments

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "suggestion"
  
  - type: word_count
    weight: 1.0
    params:
      min_words: 5
      max_words: 100
  
  - type: sentiment_positive
    weight: 1.0
    params: {}
```

#### Educational Content Template
```yaml
name: educational_content
description: Evaluates educational explanations

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "example"
  
  - type: word_count
    weight: 1.0
    params:
      min_words: 50
      max_words: 200
  
  - type: cosine_sim
    weight: 1.5
    params:
      target: "clear explanation tutorial guide"
```

---

## 🤖 Training Models

Training uses your templates to improve AI models.

### Before You Start Training

**Prerequisites**:
- Working template (tested with `clarity score`)
- Sufficient disk space (2-5 GB for model files)
- Time (training can take 30 minutes to several hours)

### Training Process Overview

1. **Model Loading**: ClarityAI downloads the base AI model
2. **Text Generation**: Model generates sample responses
3. **Scoring**: Your template scores each response
4. **Learning**: Model learns from high-scoring examples
5. **Iteration**: Process repeats for specified steps

### Basic Training Command

```bash
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20
```

### Training Parameters Explained

- `--model`: Which AI model to train (start with `microsoft/DialoGPT-small`)
- `--template`: Your scoring template file
- `--steps`: Number of training iterations (start with 20)
- `--learning-rate`: How fast the model learns (default is usually good)
- `--batch-size`: How many examples to process at once (default is usually good)
- `--output`: Where to save the trained model (default: `runs` folder)

### Training Workflow

**Step 1: Prepare Your Template**
- Test thoroughly with `clarity score`
- Make sure it gives reasonable scores
- Save the template file

**Step 2: Start Training**
```bash
clarity train --model microsoft/DialoGPT-small --template my-template.yaml --steps 20
```

**Step 3: Monitor Progress**
- Training will show progress updates
- Look for increasing reward scores
- Training creates a new folder in `runs/`

**Step 4: Review Results**
- Check the training log file
- Test the trained model with `clarity demo`
- Compare before/after performance

### Understanding Training Output

**During Training**:
```
🚀 Starting ClarityAI training...
Model: microsoft/DialoGPT-small
Template: my-template.yaml
Steps: 20
--------------------------------------------------
Step 1/20: Reward = 0.234
Step 2/20: Reward = 0.267
...
Step 20/20: Reward = 0.445
```

**After Training**:
```
✅ Training completed successfully!
Run ID: run_20250124_143022
Total steps: 20
Average reward: 0.334
Final reward: 0.445
Output directory: runs/run_20250124_143022
```

### Training Tips

1. **Start Small**: Use 20 steps for your first training
2. **Monitor Rewards**: Rewards should generally increase
3. **Save Everything**: Training creates backup files automatically
4. **Test Results**: Use `clarity demo` to see if training worked
5. **Iterate**: Adjust template and retrain if needed

---

## 🔍 Troubleshooting

This section covers common problems and their solutions.

### Installation Problems

#### Problem: `pip install -e .` fails
**Symptoms**: Error messages during installation
**Solutions**:
1. Check Python version: `python --version` (must be 3.9+)
2. Update pip: `pip install --upgrade pip`
3. Try with user flag: `pip install -e . --user`

#### Problem: `clarity` command not found
**Symptoms**: "command not found" error
**Solutions**:
1. Reinstall: `pip install -e .`
2. Check PATH: `echo $PATH`
3. Try full path: `python -m clarity.cli --help`

### Template Problems

#### Problem: Template parsing error
**Symptoms**: "Template Error" message
**Solutions**:
1. Check YAML syntax (spaces, not tabs)
2. Verify all required fields are present
3. Use online YAML validator
4. Copy from working example

#### Problem: Rules not working as expected
**Symptoms**: Unexpected scores
**Solutions**:
1. Test one rule at a time
2. Use `--detailed` flag to see rule breakdown
3. Check parameter spelling and values
4. Verify rule type is supported

### Scoring Problems

#### Problem: All scores are 0.0
**Symptoms**: Every text gets score 0.0
**Solutions**:
1. Check if template file exists
2. Verify template has rules with weight > 0
3. Test with simple text that should match rules
4. Check file permissions

#### Problem: Inconsistent scores
**Symptoms**: Same text gets different scores
**Solutions**:
1. Check for random elements in rules
2. Verify template file hasn't changed
3. Restart if using web interface
4. Check for special characters in text

### Training Problems

#### Problem: Training fails to start
**Symptoms**: Error before training begins
**Solutions**:
1. Check template file exists and is valid
2. Verify model name is correct
3. Ensure sufficient disk space
4. Check internet connection for model download

#### Problem: Training stops unexpectedly
**Symptoms**: Training exits with error
**Solutions**:
1. Check available memory (training uses 2-4 GB)
2. Reduce batch size: `--batch-size 8`
3. Use smaller model: `microsoft/DialoGPT-small`
4. Check training logs for specific errors

### Web Interface Problems

#### Problem: Web interface won't start
**Symptoms**: `streamlit run app.py` fails
**Solutions**:
1. Install streamlit: `pip install streamlit`
2. Check if port 8501 is available
3. Try different port: `streamlit run app.py --server.port 8502`
4. Check firewall settings

#### Problem: Changes not saving
**Symptoms**: Template edits disappear
**Solutions**:
1. Use "Download Template" button to save
2. Copy template text to separate file
3. Refresh browser and try again
4. Check browser console for errors

### Getting More Help

If these solutions don't work:

1. **Check Error Messages**: Read the full error message carefully
2. **Try Minimal Example**: Use the simplest possible template and text
3. **Check File Paths**: Ensure all file paths are correct and files exist
4. **Restart Everything**: Close terminal, restart, try again
5. **Check Dependencies**: Run `pip list` to see installed packages

---

## 📞 Getting Help

### Self-Help Resources

1. **This Documentation**: Start here for most questions
2. **Example Files**: Look in `templates/` folder for working examples
3. **Test Files**: Check `tests/` folder for usage patterns
4. **Error Messages**: Read error messages carefully - they often contain the solution

### When to Seek Help

Seek additional help if:
- You've tried the troubleshooting steps
- Error messages are unclear
- You need to implement custom rule types
- You want to integrate ClarityAI with other tools

### How to Ask for Help

When asking for help, include:

1. **What you were trying to do**: "I was trying to create a template for..."
2. **What you expected**: "I expected the score to be..."
3. **What actually happened**: "Instead, I got this error..."
4. **Your environment**: Operating system, Python version
5. **Exact commands**: Copy and paste the exact commands you ran
6. **Error messages**: Copy and paste the full error message

### Example Help Request

```
I'm trying to create a template for scoring code comments, but I'm getting 
a parsing error.

Expected: Template should load successfully
Actual: Getting "Template Error: mapping values are not allowed here"

Environment: macOS, Python 3.10
Command: clarity score test.txt --template code-review.yaml

Template file:
[paste your template here]

Error message:
[paste full error message here]
```

---

## 📚 Additional Resources

### File Structure Reference
```
clarity-ai/
├── clarity/           # Main package
│   ├── cli.py        # Command line interface
│   ├── scorer.py     # Scoring engine
│   └── trainer.py    # Training system
├── templates/        # Example templates
├── tests/           # Test files
├── docs/            # This documentation
├── app.py           # Web interface
└── setup.py         # Installation configuration
```

### Quick Reference Commands
```bash
# Installation
pip install -e .

# Basic scoring
clarity score text.txt --template template.yaml

# Detailed scoring
clarity score text.txt --template template.yaml --detailed

# Web interface
streamlit run app.py

# Create template
clarity create-template --name "my-template" --output my-template.yaml

# Training
clarity train --model microsoft/DialoGPT-small --template template.yaml --steps 20
```

### Template Quick Reference
```yaml
name: template_name
description: Template description

rules:
  - type: contains_phrase    # Check for specific phrase
    weight: 2.0
    params:
      phrase: "helpful"
  
  - type: word_count        # Check text length
    weight: 1.0
    params:
      min_words: 10
      max_words: 50
  
  - type: sentiment_positive # Check for positive language
    weight: 1.5
    params: {}
  
  - type: regex_match       # Pattern matching
    weight: 1.0
    params:
      pattern: "[A-Z][a-z]+"
  
  - type: cosine_sim        # Similarity to target
    weight: 1.0
    params:
      target: "machine learning"
```

---

**Remember**: Take your time with each step. This documentation is designed to be followed sequentially. Don't skip steps, and don't hesitate to re-read sections if needed.