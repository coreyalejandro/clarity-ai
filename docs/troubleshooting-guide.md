# ClarityAI Troubleshooting Guide

> **Designed for Neurodivergent Users**: This guide provides systematic, step-by-step solutions with clear verification steps. Each solution includes multiple approaches and clear success/failure indicators.

## 🎯 How to Use This Guide

1. **Find your problem** in the table of contents
2. **Follow ALL steps** in the exact order given
3. **Verify each step** before moving to the next
4. **Don't skip steps** even if they seem obvious
5. **Try all solutions** before moving to the next problem

---

## 📋 Table of Contents

1. [🔧 Installation Problems](#installation-problems)
2. [⌨️ Command Line Problems](#command-line-problems)
3. [📝 Template Problems](#template-problems)
4. [🎯 Scoring Problems](#scoring-problems)
5. [🌐 Web Interface Problems](#web-interface-problems)
6. [🤖 Training Problems](#training-problems)
7. [📁 File and Path Problems](#file-and-path-problems)
8. [🔄 System and Environment Problems](#system-and-environment-problems)

---

## 🔧 Installation Problems

### Problem 1: `pip install -e .` fails with error

**Symptoms:**
- Error messages during installation
- Installation stops before completing
- "Permission denied" errors

**Solution A: Check Python Version**

Step 1: Check your Python version
```bash
python --version
```

Step 2: Verify version is 3.9 or higher
- ✅ Good: "Python 3.9.x", "Python 3.10.x", "Python 3.11.x"
- ❌ Bad: "Python 2.x.x", "Python 3.8.x" or lower

Step 3: If version is wrong, install correct Python
- Go to python.org
- Download Python 3.9 or newer
- Install and restart terminal

**Solution B: Update pip**

Step 1: Update pip to latest version
```bash
pip install --upgrade pip
```

Step 2: Wait for completion (may take 1-2 minutes)

Step 3: Verify pip updated
```bash
pip --version
```

Step 4: Retry ClarityAI installation
```bash
pip install -e .
```

**Solution C: User Installation**

Step 1: Try installing for current user only
```bash
pip install -e . --user
```

Step 2: If successful, add to PATH (may be needed)
- On Mac/Linux: Add `~/.local/bin` to PATH
- On Windows: Add `%APPDATA%\Python\Scripts` to PATH

**Solution D: Virtual Environment**

Step 1: Create virtual environment
```bash
python -m venv clarity-env
```

Step 2: Activate virtual environment
- Mac/Linux: `source clarity-env/bin/activate`
- Windows: `clarity-env\Scripts\activate`

Step 3: Install in virtual environment
```bash
pip install -e .
```

**Verification**: Run `clarity --help` and see help message

---

### Problem 2: `clarity` command not found after installation

**Symptoms:**
- "command not found" or "not recognized" error
- Installation seemed successful
- `pip list` shows clarity-ai installed

**Solution A: Check Installation Path**

Step 1: Find where clarity was installed
```bash
pip show clarity-ai
```

Step 2: Look for "Location:" in output

Step 3: Check if location is in PATH
```bash
echo $PATH
```

**Solution B: Use Python Module**

Step 1: Try running as Python module
```bash
python -m clarity.cli --help
```

Step 2: If this works, create alias (optional)
- Add to ~/.bashrc or ~/.zshrc: `alias clarity='python -m clarity.cli'`

**Solution C: Reinstall with --force**

Step 1: Uninstall first
```bash
pip uninstall clarity-ai
```

Step 2: Reinstall
```bash
pip install -e . --force-reinstall
```

**Verification**: Run `clarity --help` and see help message

---

## ⌨️ Command Line Problems

### Problem 3: "No such file or directory" errors

**Symptoms:**
- Error when trying to score text files
- "FileNotFoundError" messages
- Commands work but can't find files

**Solution A: Check File Existence**

Step 1: Verify file exists
```bash
ls -la your-file.txt
```

Step 2: If file doesn't exist, create it or fix the path

Step 3: Check current directory
```bash
pwd
```

Step 4: Make sure you're in the right directory

**Solution B: Use Absolute Paths**

Step 1: Get full path to file
```bash
realpath your-file.txt
```

Step 2: Use full path in command
```bash
clarity score /full/path/to/your-file.txt --template /full/path/to/template.yaml
```

**Solution C: Check File Permissions**

Step 1: Check file permissions
```bash
ls -la your-file.txt
```

Step 2: If no read permission, fix it
```bash
chmod +r your-file.txt
```

**Verification**: Command runs without file errors

---

### Problem 4: Template file errors

**Symptoms:**
- "Template file not found" errors
- Template loads but gives parsing errors
- Rules don't work as expected

**Solution A: Verify Template File**

Step 1: Check template file exists
```bash
ls -la your-template.yaml
```

Step 2: Check file contents
```bash
cat your-template.yaml
```

Step 3: Verify YAML syntax online
- Go to yamllint.com
- Paste your template
- Fix any syntax errors

**Solution B: Use Demo Template First**

Step 1: Test with known good template
```bash
clarity score your-text.txt --template templates/demo.yaml
```

Step 2: If this works, problem is with your template

Step 3: Compare your template to demo template structure

**Solution C: Create Minimal Template**

Step 1: Create simple test template
```yaml
name: test_template
description: Simple test

rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "test"
```

Step 2: Save as `test-template.yaml`

Step 3: Test with simple text containing "test"

**Verification**: Template loads without errors and produces scores

---

## 📝 Template Problems

### Problem 5: YAML parsing errors

**Symptoms:**
- "mapping values are not allowed here"
- "could not find expected ':'"
- "found character that cannot start any token"

**Solution A: Check Indentation**

Step 1: Verify you're using spaces, not tabs
- Open template in text editor
- Show whitespace characters
- Replace any tabs with spaces

Step 2: Check indentation levels
```yaml
name: template_name          # No indentation
description: description     # No indentation

rules:                       # No indentation
  - type: rule_type         # 2 spaces
    weight: 1.0             # 4 spaces
    params:                 # 4 spaces
      parameter: value      # 6 spaces
```

**Solution B: Check Special Characters**

Step 1: Look for problematic characters
- Curly quotes (" ") instead of straight quotes (" ")
- Em dashes (—) instead of hyphens (-)
- Non-ASCII spaces

Step 2: Replace with standard ASCII characters

**Solution C: Use Template Validator**

Step 1: Copy template to online YAML validator
- Go to yamllint.com or yamlchecker.com
- Paste your template
- Fix reported errors

Step 2: Test fixed template
```bash
clarity score test-text.txt --template fixed-template.yaml
```

**Verification**: Template loads without parsing errors

---

### Problem 6: Rules not working as expected

**Symptoms:**
- All rules score 0.0
- Rules that should match don't match
- Unexpected scores

**Solution A: Test One Rule at a Time**

Step 1: Create template with single rule
```yaml
name: single_rule_test
description: Testing one rule

rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: "test"
```

Step 2: Test with text containing "test"
```bash
clarity score --text "This is a test" --template single-rule-test.yaml --detailed
```

Step 3: Verify rule works (should score 1.0)

Step 4: Add rules one by one and test each

**Solution B: Check Rule Parameters**

Step 1: Verify parameter names are correct
- `contains_phrase`: needs `phrase`
- `word_count`: needs `min_words` and `max_words`
- `sentiment_positive`: needs empty `params: {}`
- `regex_match`: needs `pattern`
- `cosine_sim`: needs `target`

Step 2: Check parameter values
- Strings should be in quotes
- Numbers should not be in quotes
- Boolean values: true/false (lowercase)

**Solution C: Debug with Simple Examples**

Step 1: Test each rule type with obvious examples

For `contains_phrase`:
```bash
clarity score --text "This text contains the word helpful" --template template.yaml --detailed
```

For `word_count` (10-20 words):
```bash
clarity score --text "This sentence has exactly fifteen words in it to test the word count rule" --template template.yaml --detailed
```

For `sentiment_positive`:
```bash
clarity score --text "This is wonderful, amazing, and fantastic!" --template template.yaml --detailed
```

**Verification**: Each rule produces expected scores with test cases

---

## 🎯 Scoring Problems

### Problem 7: All scores are 0.0

**Symptoms:**
- Every text gets score 0.0
- Rules show 0.0 in detailed breakdown
- No errors reported

**Solution A: Check Rule Weights**

Step 1: Verify weights are greater than 0
```yaml
rules:
  - type: contains_phrase
    weight: 1.0  # Must be > 0
    params:
      phrase: "test"
```

Step 2: Check total weight calculation
- If all rules fail, total score will be 0.0
- At least one rule must succeed for non-zero score

**Solution B: Test with Guaranteed Matches**

Step 1: Create text that definitely matches your rules
- If looking for "helpful", use text with "helpful"
- If checking word count 10-50, use text with 25 words
- If checking positive sentiment, use very positive text

Step 2: Test with this guaranteed match text

**Solution C: Check Rule Logic**

Step 1: Test each rule type individually

For `word_count`, count words manually:
```bash
echo "your test text here" | wc -w
```

For `contains_phrase`, search manually:
```bash
echo "your test text" | grep -i "search phrase"
```

**Verification**: At least some rules produce non-zero scores

---

### Problem 8: Inconsistent scores for same text

**Symptoms:**
- Same text gets different scores on different runs
- Scores vary without changing template or text
- Results not reproducible

**Solution A: Check for Random Elements**

Step 1: Look for rules that might have randomness
- `sentiment_positive` can vary slightly
- Some regex patterns might be non-deterministic

Step 2: Test multiple times with simple rules
```bash
clarity score --text "test text" --template simple-template.yaml
clarity score --text "test text" --template simple-template.yaml
clarity score --text "test text" --template simple-template.yaml
```

**Solution B: Restart Everything**

Step 1: Close all terminals and applications

Step 2: Restart terminal

Step 3: Navigate back to project directory

Step 4: Test again

**Solution C: Check File Changes**

Step 1: Verify template file hasn't changed
```bash
cat your-template.yaml
```

Step 2: Verify text file hasn't changed
```bash
cat your-text.txt
```

Step 3: Check file timestamps
```bash
ls -la your-template.yaml your-text.txt
```

**Verification**: Same input produces same output consistently

---

## 🌐 Web Interface Problems

### Problem 9: Web interface won't start

**Symptoms:**
- `streamlit run app.py` fails
- Browser doesn't open
- Connection errors

**Solution A: Check Streamlit Installation**

Step 1: Verify streamlit is installed
```bash
pip list | grep streamlit
```

Step 2: If not installed, install it
```bash
pip install streamlit
```

Step 3: Try starting again
```bash
streamlit run app.py
```

**Solution B: Check Port Availability**

Step 1: Try different port
```bash
streamlit run app.py --server.port 8502
```

Step 2: If successful, use new URL: `http://localhost:8502`

Step 3: Check what's using port 8501
```bash
lsof -i :8501
```

**Solution C: Manual Browser Opening**

Step 1: Start streamlit and note the URL in output

Step 2: Manually open browser

Step 3: Go to the URL shown (usually `http://localhost:8501`)

**Verification**: Web interface loads and shows ClarityAI interface

---

### Problem 10: Web interface loads but doesn't work

**Symptoms:**
- Interface appears but buttons don't work
- Template editor doesn't update
- Scoring doesn't produce results

**Solution A: Check Browser Console**

Step 1: Open browser developer tools (F12)

Step 2: Look at Console tab for errors

Step 3: Refresh page and check for new errors

Step 4: Try different browser (Chrome, Firefox, Safari)

**Solution B: Clear Browser Cache**

Step 1: Clear browser cache and cookies

Step 2: Restart browser

Step 3: Go to interface URL again

**Solution C: Restart Streamlit**

Step 1: Stop streamlit (Ctrl+C in terminal)

Step 2: Wait 5 seconds

Step 3: Restart streamlit
```bash
streamlit run app.py
```

**Verification**: All interface features work correctly

---

## 🤖 Training Problems

### Problem 11: Training fails to start

**Symptoms:**
- Error before training begins
- "Model not found" errors
- Dependency errors

**Solution A: Check Dependencies**

Step 1: Install training dependencies
```bash
pip install torch transformers trl datasets
```

Step 2: Verify installation
```bash
python -c "import torch, transformers, trl; print('All dependencies installed')"
```

**Solution B: Check Model Name**

Step 1: Use known working model
```bash
clarity train --model microsoft/DialoGPT-small --template your-template.yaml --steps 5
```

Step 2: If this works, your original model name was wrong

**Solution C: Check Internet Connection**

Step 1: Test internet connection
```bash
ping google.com
```

Step 2: Models are downloaded from internet on first use

Step 3: Ensure firewall allows Python internet access

**Verification**: Training starts and shows progress

---

### Problem 12: Training stops unexpectedly

**Symptoms:**
- Training starts but crashes
- "Out of memory" errors
- Training stops without completion

**Solution A: Reduce Memory Usage**

Step 1: Use smaller batch size
```bash
clarity train --model microsoft/DialoGPT-small --template template.yaml --batch-size 4 --steps 10
```

Step 2: Use smaller model
```bash
clarity train --model distilgpt2 --template template.yaml --steps 10
```

**Solution B: Check Available Memory**

Step 1: Check system memory
- Mac: Activity Monitor
- Windows: Task Manager
- Linux: `free -h`

Step 2: Close other applications

Step 3: Restart training

**Solution C: Reduce Training Steps**

Step 1: Start with very few steps
```bash
clarity train --model microsoft/DialoGPT-small --template template.yaml --steps 5
```

Step 2: If successful, gradually increase steps

**Verification**: Training completes successfully

---

## 📁 File and Path Problems

### Problem 13: "Permission denied" errors

**Symptoms:**
- Can't read or write files
- "Permission denied" when accessing files
- Commands fail with access errors

**Solution A: Check File Permissions**

Step 1: Check current permissions
```bash
ls -la your-file.txt
```

Step 2: Add read permission if needed
```bash
chmod +r your-file.txt
```

Step 3: Add write permission if needed
```bash
chmod +w your-file.txt
```

**Solution B: Check Directory Permissions**

Step 1: Check directory permissions
```bash
ls -la .
```

Step 2: Ensure you can write to current directory
```bash
touch test-file.txt
rm test-file.txt
```

**Solution C: Use Different Location**

Step 1: Try working in your home directory
```bash
cd ~
mkdir clarity-work
cd clarity-work
```

Step 2: Copy files to this location

Step 3: Run commands from here

**Verification**: Files can be read and written without errors

---

### Problem 14: Path with spaces causes errors

**Symptoms:**
- Errors when file paths contain spaces
- Commands work with some files but not others
- "No such file" errors for files that exist

**Solution A: Use Quotes**

Step 1: Put file paths in quotes
```bash
clarity score "my file with spaces.txt" --template "my template.yaml"
```

**Solution B: Escape Spaces**

Step 1: Use backslash before spaces
```bash
clarity score my\ file\ with\ spaces.txt --template my\ template.yaml
```

**Solution C: Rename Files**

Step 1: Rename files to remove spaces
```bash
mv "my file.txt" "my-file.txt"
mv "my template.yaml" "my-template.yaml"
```

**Verification**: Commands work with all file paths

---

## 🔄 System and Environment Problems

### Problem 15: Different results on different computers

**Symptoms:**
- Same template and text give different scores
- Commands work on one computer but not another
- Inconsistent behavior across systems

**Solution A: Check Python Versions**

Step 1: Check Python version on both systems
```bash
python --version
```

Step 2: Ensure both use Python 3.9+

Step 3: Check package versions
```bash
pip list
```

**Solution B: Check File Encoding**

Step 1: Ensure files use UTF-8 encoding

Step 2: Re-save files with UTF-8 encoding

Step 3: Check for hidden characters
```bash
cat -A your-file.txt
```

**Solution C: Reinstall on Problem System**

Step 1: Uninstall ClarityAI
```bash
pip uninstall clarity-ai
```

Step 2: Clean install
```bash
pip install -e .
```

**Verification**: Both systems produce identical results

---

## 🆘 Emergency Troubleshooting

### When Nothing Works

**Step 1: Complete Reset**

1. Close all terminals and applications
2. Restart your computer
3. Open fresh terminal
4. Navigate to ClarityAI directory
5. Try basic command: `clarity --help`

**Step 2: Minimal Test**

1. Create simple text file: `echo "test" > simple.txt`
2. Use demo template: `clarity score simple.txt --template templates/demo.yaml`
3. If this works, problem is with your custom files

**Step 3: Clean Reinstall**

1. Uninstall: `pip uninstall clarity-ai`
2. Delete any cached files: `rm -rf ~/.cache/pip`
3. Reinstall: `pip install -e .`
4. Test: `clarity --help`

**Step 4: Check System Requirements**

1. Python 3.9+: `python --version`
2. Sufficient disk space: `df -h`
3. Internet connection: `ping google.com`
4. No antivirus blocking: Check antivirus logs

---

## 📞 Getting Additional Help

### Before Asking for Help

Collect this information:

1. **Operating System**: Mac, Windows, Linux (which version?)
2. **Python Version**: Output of `python --version`
3. **ClarityAI Version**: Output of `pip show clarity-ai`
4. **Exact Command**: Copy and paste the exact command you ran
5. **Full Error Message**: Copy and paste the complete error
6. **What You Expected**: What should have happened?
7. **Files Used**: Content of template and text files (if relevant)

### Example Help Request

```
System: macOS 12.6, Python 3.10.8, ClarityAI 0.1.0

Command: clarity score test.txt --template my-template.yaml --detailed

Error: 
Template Error: mapping values are not allowed here
  in "my-template.yaml", line 4, column 15

Expected: Template should load and score the text

Template file content:
name: my_template
description: Test template
rules:
  - type: contains_phrase
    weight: 1.0
    params:
      phrase: helpful

Text file content:
This is a helpful guide for beginners.
```

This format helps others understand and solve your problem quickly.

---

**Remember**: Take your time with each solution. Complete all steps in order. Don't skip steps even if they seem obvious. Most problems have multiple possible causes, so try all solutions if the first one doesn't work.