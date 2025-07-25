# ClarityAI Step-by-Step Tutorial

> **CRITICAL**: This tutorial is designed for neurodivergent learners. Each step must be completed in order. Do not skip any steps. Each step includes verification to ensure you're on the right track.

## 🎯 Tutorial Goals

By the end of this tutorial, you will:
1. Have ClarityAI installed and working
2. Understand how templates work
3. Create your own scoring template
4. Test your template with sample text
5. Use the web interface confidently

**Estimated Time**: 45-60 minutes
**Prerequisites**: Computer with internet access, basic text editing skills

---

## 📋 Pre-Tutorial Checklist

Before starting, verify you have:
- [ ] Python 3.9 or newer installed
- [ ] Terminal/Command Prompt access
- [ ] Text editor (Notepad, TextEdit, VS Code, etc.)
- [ ] Internet connection
- [ ] At least 2 GB free disk space

**How to check Python version**:
1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type: `python --version`
3. Press Enter
4. You should see something like "Python 3.9.x" or higher

❌ **If Python version is wrong**: Install Python 3.9+ before continuing

---

## 🔧 Step 1: Installation

### Step 1.1: Navigate to Project Directory

**Action**: Open Terminal and go to your ClarityAI folder

**Commands**:
```bash
cd /path/to/clarity-ai
```

**Replace `/path/to/clarity-ai` with your actual folder path**

**Verification**: Type `ls` (Mac/Linux) or `dir` (Windows) and press Enter. You should see files like:
- `app.py`
- `setup.py` 
- `clarity/` folder
- `README.md`

❌ **If you don't see these files**: You're in the wrong directory. Navigate to the correct ClarityAI folder.

### Step 1.2: Install ClarityAI

**Action**: Install the ClarityAI package

**Command**:
```bash
pip install -e .
```

**What this does**: Downloads and installs all required components

**Expected output**: You'll see text scrolling by for 2-5 minutes, ending with something like:
```
Successfully installed clarity-ai-0.1.0
```

**Verification**: Type `clarity --help` and press Enter. You should see a help message.

❌ **If installation fails**: 
1. Try: `pip install --upgrade pip`
2. Then retry: `pip install -e .`
3. If still failing, try: `pip install -e . --user`

### Step 1.3: Verify Installation

**Action**: Test that ClarityAI is working

**Command**:
```bash
clarity --help
```

**Expected output**:
```
usage: clarity [-h] {score,demo,create-template,train} ...

ClarityAI - Train LLMs with teacher-style rubrics
...
```

✅ **Success indicator**: You see the help message with available commands

❌ **If you see "command not found"**: Installation didn't work. Go back to Step 1.2.

---

## 📝 Step 2: Understanding Templates

### Step 2.1: Look at Example Template

**Action**: Examine the demo template to understand structure

**Command**:
```bash
cat templates/demo.yaml
```

**What you'll see**: A YAML file with template structure

**Key parts to notice**:
- `name:` - Template identifier
- `description:` - What the template does
- `rules:` - List of scoring criteria
- Each rule has `type`, `weight`, and `params`

### Step 2.2: Understand Rule Types

**Study these rule types** (you'll use them later):

1. **contains_phrase**: Looks for specific words/phrases
2. **word_count**: Checks if text has right number of words
3. **sentiment_positive**: Detects positive language
4. **regex_match**: Matches patterns
5. **cosine_sim**: Measures similarity to target text

**Action**: Read each rule in the demo template and try to understand what it does.

---

## 🎯 Step 3: Your First Scoring Test

### Step 3.1: Create Test Text File

**Action**: Create a simple text file to test with

**Steps**:
1. Open your text editor
2. Type this text exactly:
```
This is a helpful guide that explains programming concepts clearly. It provides good examples and is easy to understand.
```
3. Save as `test-text.txt` in your ClarityAI folder

**Verification**: The file should be in the same folder as `app.py`

### Step 3.2: Score Your Text

**Action**: Use ClarityAI to score your test text

**Command**:
```bash
clarity score test-text.txt --template templates/demo.yaml --detailed
```

**Expected output**:
```
Overall Score: [some number between 0.0 and 1.0]
Total Weight: [sum of all rule weights]

Rule Breakdown:
  ✓ [rule name] (weight: [number]): [score] → [weighted score]
  ✓ [rule name] (weight: [number]): [score] → [weighted score]
  ...
```

### Step 3.3: Understand Your Results

**Action**: Analyze what each part means

**Overall Score**: This is your final score (0.0 = terrible, 1.0 = perfect)
**Rule Breakdown**: Shows how each rule contributed

**For each rule**:
- ✓ means the rule worked
- ❌ means there was an error
- First number is raw score (0.0-1.0)
- Second number is weighted score (raw score × weight)

**Verification**: You should see at least some rules with ✓ marks

❌ **If all rules show errors**: Check that your text file was created correctly

---

## 🛠️ Step 4: Create Your Own Template

### Step 4.1: Plan Your Template

**Action**: Decide what you want to score

**Example scenarios**:
- Code comments (should be helpful and clear)
- Email responses (should be polite and informative)
- Product descriptions (should be detailed and positive)

**For this tutorial, we'll create a "helpful explanation" template**

### Step 4.2: Create Template File

**Action**: Create a new template file

**Steps**:
1. Open your text editor
2. Copy this template exactly (including all spaces):

```yaml
name: helpful_explanation
description: Scores text based on how helpful and clear it is

rules:
  - type: contains_phrase
    weight: 2.0
    params:
      phrase: "helpful"

  - type: contains_phrase
    weight: 1.5
    params:
      phrase: "clear"

  - type: word_count
    weight: 1.0
    params:
      min_words: 15
      max_words: 100

  - type: sentiment_positive
    weight: 1.0
    params: {}
```

3. Save as `my-template.yaml` in your ClarityAI folder

**Critical**: Make sure spacing is exact. YAML is very sensitive to spaces.

### Step 4.3: Test Your Template

**Action**: Verify your template works

**Command**:
```bash
clarity score test-text.txt --template my-template.yaml --detailed
```

**Expected result**: You should see scores for all 4 rules

✅ **Success indicators**:
- No error messages
- All rules show ✓ marks
- You get an overall score

❌ **If you see parsing errors**:
1. Check that all spaces are correct (no tabs)
2. Verify all colons and dashes are in the right places
3. Make sure `params: {}` has the curly braces

### Step 4.4: Understand Your Template Results

**Action**: Analyze how your template scored the text

**Your text was**: "This is a helpful guide that explains programming concepts clearly..."

**Expected rule results**:
- `contains_phrase "helpful"`: Should score 1.0 (found "helpful")
- `contains_phrase "clear"`: Should score 1.0 (found "clearly")  
- `word_count 15-100`: Should score 1.0 (text has ~17 words)
- `sentiment_positive`: Should score 0.7-0.9 (positive language)

**Verification**: Your results should roughly match these expectations

---

## 🌐 Step 5: Using the Web Interface

### Step 5.1: Start the Web Interface

**Action**: Launch the visual interface

**Command**:
```bash
streamlit run app.py
```

**Expected result**: 
- Terminal shows "You can now view your Streamlit app in your browser"
- Browser opens automatically to `http://localhost:8501`

❌ **If browser doesn't open**: Manually go to `http://localhost:8501`

### Step 5.2: Load Your Template

**Action**: Get your template into the web interface

**Steps**:
1. In the web interface, look at the left panel "📝 Rubric Editor"
2. Find "Template Management" section
3. Select "Load from File"
4. Click "Browse files" and select your `my-template.yaml`
5. You should see your template appear in the "Template Editor" box below

**Verification**: You should see ✅ "Template 'helpful_explanation' loaded successfully"

### Step 5.3: Test with Web Interface

**Action**: Score text using the visual interface

**Steps**:
1. Look at the right panel "🚀 Live Scoring"
2. In "Text Input" section, select "Type Custom Text"
3. In the text box, type:
```
This helpful tutorial provides clear instructions for beginners. The examples are easy to follow and understand.
```
4. Click the "🎯 Score Text" button
5. Look at the results below

**Expected results**:
- Overall Score appears (should be high, around 0.8-1.0)
- Rule Breakdown shows each rule's contribution
- Score History chart appears (if you score multiple times)

### Step 5.4: Experiment with Different Text

**Action**: Try different inputs to see how scores change

**Test these examples**:

**Example 1** (should score high):
```
This is a helpful and clear explanation with good examples.
```

**Example 2** (should score lower):
```
Bad explanation. Confusing and unhelpful.
```

**Example 3** (should score medium):
```
This explanation covers the topic but could be clearer and more detailed for better understanding.
```

**Verification**: Scores should vary based on content (Example 1 > Example 3 > Example 2)

---

## 🔧 Step 6: Customizing Your Template

### Step 6.1: Modify Template in Web Interface

**Action**: Edit your template using the visual editor

**Steps**:
1. In the web interface, find the "Template Editor" text box
2. Find the line with `phrase: "helpful"`
3. Change it to `phrase: "excellent"`
4. The template should automatically reload
5. Test with text containing "excellent" vs "helpful"

**Expected result**: Text with "excellent" should now score higher than text with "helpful"

### Step 6.2: Add a New Rule

**Action**: Add another scoring criterion

**Steps**:
1. In the Template Editor, add this new rule at the end (before the last line):

```yaml
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "example"
```

2. Make sure the spacing matches the other rules
3. Test with text that contains "example"

**Verification**: You should now see 5 rules in the Rule Breakdown

### Step 6.3: Adjust Weights

**Action**: Change rule importance

**Steps**:
1. Change the weight of `sentiment_positive` from `1.0` to `3.0`
2. Test the same text as before
3. Notice how the overall score changes

**Expected result**: Positive text should now score higher because sentiment has more weight

### Step 6.4: Save Your Modified Template

**Action**: Download your customized template

**Steps**:
1. Click the "💾 Download Template" button
2. Save as `my-custom-template.yaml`
3. Test it with the command line:

```bash
clarity score test-text.txt --template my-custom-template.yaml --detailed
```

**Verification**: Command line results should match web interface results

---

## 🎓 Step 7: Advanced Testing

### Step 7.1: Batch Testing

**Action**: Test multiple texts at once

**Steps**:
1. In the web interface, go to "Text Input" section
2. Select "Use Sample Texts"
3. Scroll down to "Batch Scoring" section
4. Click "📊 Score All Samples"
5. Review the results table

**What to observe**: Different sample texts get different scores based on your template

### Step 7.2: Create Test Cases

**Action**: Create specific texts to test each rule

**Create these test files**:

**File 1**: `test-helpful.txt`
```
This helpful guide explains everything clearly with excellent examples.
```

**File 2**: `test-no-keywords.txt`
```
This document discusses various topics and provides information about different subjects.
```

**File 3**: `test-too-short.txt`
```
Short text.
```

**Test each file**:
```bash
clarity score test-helpful.txt --template my-custom-template.yaml --detailed
clarity score test-no-keywords.txt --template my-custom-template.yaml --detailed
clarity score test-too-short.txt --template my-custom-template.yaml --detailed
```

**Expected results**:
- `test-helpful.txt`: High score (should hit most rules)
- `test-no-keywords.txt`: Medium score (word count ok, but missing keywords)
- `test-too-short.txt`: Low score (too few words, missing keywords)

---

## ✅ Step 8: Verification and Next Steps

### Step 8.1: Final Verification Checklist

Verify you can do all of these:

- [ ] Install ClarityAI successfully
- [ ] Run `clarity --help` and see help message
- [ ] Score text files using command line
- [ ] Create and edit template files
- [ ] Use the web interface to test templates
- [ ] Modify templates and see score changes
- [ ] Save and load custom templates

### Step 8.2: Understanding Check

**Answer these questions** (answers at bottom):

1. What does a score of 0.0 mean?
2. What does a score of 1.0 mean?
3. If a rule has weight 2.0 and raw score 0.5, what's the weighted score?
4. Which rule type would you use to check if text contains the word "python"?
5. Which rule type would you use to ensure text is 20-50 words long?

### Step 8.3: Next Steps

Now that you've completed the tutorial, you can:

1. **Create domain-specific templates**: Make templates for your specific use case
2. **Try model training**: Use `clarity train` to improve AI models
3. **Integrate with other tools**: Use ClarityAI in your existing workflows
4. **Explore advanced rules**: Try `regex_match` and `cosine_sim` rules

### Step 8.4: Common Next Actions

**For code review**:
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

**For educational content**:
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
```

---

## 🆘 Troubleshooting Your Tutorial

### If Step 1 (Installation) Failed:
1. Check Python version: `python --version`
2. Update pip: `pip install --upgrade pip`
3. Try user install: `pip install -e . --user`
4. Check you're in the right directory

### If Step 3 (First Test) Failed:
1. Verify `test-text.txt` exists: `ls test-text.txt`
2. Check template exists: `ls templates/demo.yaml`
3. Try absolute paths: `clarity score /full/path/to/test-text.txt --template /full/path/to/templates/demo.yaml`

### If Step 4 (Custom Template) Failed:
1. Check YAML syntax with online validator
2. Ensure no tabs (only spaces)
3. Copy template exactly from tutorial
4. Verify file saved correctly

### If Step 5 (Web Interface) Failed:
1. Install streamlit: `pip install streamlit`
2. Try different port: `streamlit run app.py --server.port 8502`
3. Check firewall settings
4. Try `http://127.0.0.1:8501` instead

---

## 📚 Tutorial Answers

**Understanding Check Answers**:
1. Score 0.0 = Text completely fails the template criteria
2. Score 1.0 = Text perfectly meets all template criteria  
3. Weighted score = 0.5 × 2.0 = 1.0
4. Use `contains_phrase` with `phrase: "python"`
5. Use `word_count` with `min_words: 20` and `max_words: 50`

---

**🎉 Congratulations!** You've completed the ClarityAI tutorial. You now have the skills to create custom scoring templates and use ClarityAI effectively for your projects.