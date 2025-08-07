# ClarityAI Visual Guide

> **Visual Learning Support**: This guide uses diagrams, flowcharts, and visual representations to supplement the main documentation.

## 📊 System Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        ClarityAI System                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Template  │    │    Text     │    │   Scoring   │      │
│  │   (Rules)   │───▶│   Input     │───▶│   Engine    │      │
│  │             │    │             │    │             │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Training  │◀───│   Results   │◀───│    Score    │      │
│  │   (Optional)│    │  & Feedback │    │  (0.0-1.0)  │      │ 
│  │             │    │             │    │             │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Workflow Flowchart

```
START
  ▼                                                                                                                           
┌─────────────────┐
│ Install         │
│ ClarityAI       │
└─────────────────┘
  ▼
┌─────────────────┐
│ Create/Load     │
│ Template        │
└─────────────────┘
  ▼
┌─────────────────┐
│ Test Template   │
│ with Sample     │
│ Text            │
└─────────────────┘
  ▼
┌─────────────────┐     ┌─────────────────┐
│ Scores Look     │ NO  │ Adjust Template │
│ Reasonable?     │────▶│ Rules & Weights │
└─────────────────┘     └─────────────────┘
  ▼ YES                           ▲
┌─────────────────┐               │
│ Use Template    │               │
│ for Scoring     │               │
│ or Training     │───────────────┘
└─────────────────┘
  ▼
END
```

## 📝 Template Structure Visual

```
Template File (YAML)
┌─────────────────────────────────────────┐
│ name: my_template                       │ ◀── Template Name
│ description: What this template does    │ ◀── Description
│                                         │
│ rules:                                  │ ◀── Rules Section Start
│   - type: contains_phrase               │ ◀── Rule Type
│     weight: 2.0                         │ ◀── Rule Weight (Importance)
│     params:                             │ ◀── Rule Parameters
│       phrase: "helpful"                 │ ◀── Specific Parameter
│                                         │
│   - type: word_count                    │ ◀── Second Rule
│     weight: 1.0                         │
│     params:                             │
│       min_words: 10                     │
│       max_words: 50                     │
│                                         │
│   - type: sentiment_positive            │ ◀── Third Rule
│     weight: 1.5                         │
│     params: {}                          │ ◀── Empty Parameters
└─────────────────────────────────────────┘
```

## 🎯 Scoring Process Visual

```
Input Text: "This is a helpful guide with clear examples."

Rule 1: contains_phrase (weight: 2.0)
┌─────────────────────────────────────────┐
│ Looking for: "helpful"                  │
│ Found: ✅ YES                           │
│ Raw Score: 1.0                          │
│ Weighted Score: 1.0 × 2.0 = 2.0        │
└─────────────────────────────────────────┘

Rule 2: word_count (weight: 1.0)
┌─────────────────────────────────────────┐
│ Word Count: 9 words                     │
│ Range: 10-50 words                      │
│ In Range: ❌ NO (too few)               │
│ Raw Score: 0.0                          │
│ Weighted Score: 0.0 × 1.0 = 0.0        │
└─────────────────────────────────────────┘

Rule 3: sentiment_positive (weight: 1.5)
┌─────────────────────────────────────────┐
│ Positive Words: "helpful", "clear"      │
│ Sentiment Analysis: Positive            │
│ Raw Score: 0.8                          │
│ Weighted Score: 0.8 × 1.5 = 1.2        │
└─────────────────────────────────────────┘

Final Calculation:
┌─────────────────────────────────────────┐
│ Total Weighted Score: 2.0 + 0.0 + 1.2 = 3.2 │
│ Total Weight: 2.0 + 1.0 + 1.5 = 4.5    │
│ Final Score: 3.2 ÷ 4.5 = 0.711         │
└─────────────────────────────────────────┘
```

## 🖥️ Web Interface Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                        🎯 ClarityAI                                 │
│                 Train LLMs with teacher-style rubrics              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────────────────┐ │ ┌─────────────────────────────────┐   │
│ │    📝 Rubric Editor     │ │ │       🚀 Live Scoring         │   │
│ │                         │ │ │                               │   │
│ │ Template Management     │ │ │ Text Input                    │   │
│ │ ○ Use Default Template  │ │ │ ○ Type Custom Text            │   │
│ │ ○ Load from File        │ │ │ ○ Use Sample Texts            │   │
│ │ ○ Create Custom         │ │ │                               │   │
│ │                         │ │ │ ┌─────────────────────────┐   │   │
│ │ Template Editor         │ │ │ │ Enter text to score:    │   │   │
│ │ ┌─────────────────────┐ │ │ │ │                         │   │   │
│ │ │ name: my_template   │ │ │ │ │ [Text input area]       │   │   │
│ │ │ description: ...    │ │ │ │ │                         │   │   │
│ │ │ rules:              │ │ │ │ └─────────────────────────┘   │   │
│ │ │   - type: ...       │ │ │ │                               │   │
│ │ │     weight: ...     │ │ │ │ [🎯 Score Text Button]        │   │
│ │ │     params: ...     │ │ │ │                               │   │
│ │ └─────────────────────┘ │ │ │ Scoring Results               │   │
│ │                         │ │ │ Overall Score: 0.750          │   │
│ │ ✅ Template loaded      │ │ │                               │   │
│ │                         │ │ │ Rule Breakdown:               │   │
│ │ [💾 Download Template]  │ │ │ ✓ contains_phrase: 1.000      │   │
│ │                         │ │ │ ✓ word_count: 1.000           │   │
│ │                         │ │ │ ✓ sentiment_positive: 0.500   │   │
│ └─────────────────────────┘ │ └─────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Command Line Interface Visual

```
Terminal/Command Prompt
┌─────────────────────────────────────────────────────────────────────┐
│ $ clarity score test.txt --template my-template.yaml --detailed     │
│                                                                     │
│ Overall Score: 0.750                                                │
│ Total Weight: 4.5                                                   │
│                                                                     │
│ Rule Breakdown:                                                     │
│   ✓ contains_phrase (weight: 2.0): 1.000 → 2.000                   │
│   ✓ word_count (weight: 1.0): 1.000 → 1.000                        │
│   ✓ sentiment_positive (weight: 1.5): 0.500 → 0.750                │
│                                                                     │
│ $                                                                   │
└─────────────────────────────────────────────────────────────────────┘

Command Structure:
┌─────────────────────────────────────────────────────────────────────┐
│ clarity [command] [input] [options]                                 │
│    ▲        ▲        ▲        ▲                                     │
│    │        │        │        └── Additional settings              │
│    │        │        └─────────── What to process                  │
│    │        └──────────────────── What to do                       │
│    └───────────────────────────── Program name                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Training Process Visual

```
Training Steps Visualization

Step 1: Model Loading
┌─────────────────┐
│ Download Base   │
│ AI Model        │
│ ⏳ Loading...   │
└─────────────────┘

Step 2: Text Generation
┌─────────────────┐    ┌─────────────────┐
│ AI Model        │───▶│ Generated       │
│ Creates Text    │    │ Sample Texts    │
└─────────────────┘    └─────────────────┘

Step 3: Scoring
┌─────────────────┐    ┌─────────────────┐
│ Your Template   │───▶│ Scores Each     │
│ Evaluates       │    │ Generated Text  │
└─────────────────┘    └─────────────────┘

Step 4: Learning
┌─────────────────┐    ┌─────────────────┐
│ High Scores =   │───▶│ Model Learns    │
│ Good Examples   │    │ to Improve      │
└─────────────────┘    └─────────────────┘

Step 5: Repeat
┌─────────────────┐
│ Process Repeats │
│ for N Steps     │
│ (Getting Better)│
└─────────────────┘
```

## 📈 Progress Tracking Visual

```
Training Progress Example

Step:  1    5    10   15   20
Score: │    │    │    │    │
 1.0 ─ ┤    │    │    │    ●  ← Final Score
       │    │    │    ●    │
 0.8 ─ ┤    │    ●    │    │
       │    ●    │    │    │
 0.6 ─ ┤    │    │    │    │
       ●    │    │    │    │
 0.4 ─ ┤    │    │    │    │
       │    │    │    │    │
 0.2 ─ ┤    │    │    │    │
       │    │    │    │    │
 0.0 ─ └────┴────┴────┴────┘

Trend: ↗️ Improving (Good!)
```

## 🗂️ File Organization Visual

```
Project Structure
clarity-ai/
├── 📁 clarity/                    ← Main code
│   ├── 📄 __init__.py
│   ├── 📄 cli.py                  ← Command line interface
│   ├── 📄 scorer.py               ← Scoring engine
│   └── 📄 trainer.py              ← Training system
│
├── 📁 templates/                  ← Example templates
│   └── 📄 demo.yaml
│
├── 📁 tests/                      ← Test files
│   ├── 📁 unit/
│   ├── 📁 integration/
│   └── 📁 performance/
│
├── 📁 docs/                       ← Documentation
│   ├── 📄 README.md               ← Main guide
│   └── 📄 visual-guide.md         ← This file
│
├── 📁 runs/                       ← Training outputs
│   └── 📁 run_20250124_143022/
│
├── 📄 app.py                      ← Web interface
├── 📄 setup.py                    ← Installation config
└── 📄 README.md                   ← Project overview
```

## 🎨 Color-Coded Status Indicators

```
Status Indicators Guide:

✅ Success / Working / Found
❌ Error / Failed / Not Found
⚠️  Warning / Attention Needed
ℹ️  Information / Note
🔄 In Progress / Loading
⏳ Waiting / Processing
🎯 Action Required
📝 Edit / Modify
💾 Save / Download
🚀 Start / Launch
```

## 🔍 Troubleshooting Decision Tree

```
Problem Occurred?
        │
        ▼
┌─────────────────┐
│ Installation    │ YES ┌─────────────────┐
│ Problem?        │────▶│ Check Python    │
└─────────────────┘     │ Version & pip   │
        │ NO            └─────────────────┘
        ▼
┌─────────────────┐
│ Template        │ YES ┌─────────────────┐
│ Problem?        │────▶│ Check YAML      │
└─────────────────┘     │ Syntax & Rules  │
        │ NO            └─────────────────┘
        ▼
┌─────────────────┐
│ Scoring         │ YES ┌─────────────────┐
│ Problem?        │────▶│ Test with       │
└─────────────────┘     │ Simple Example  │
        │ NO            └─────────────────┘
        ▼
┌─────────────────┐
│ Training        │ YES ┌─────────────────┐
│ Problem?        │────▶│ Check Memory    │
└─────────────────┘     │ & Disk Space    │
        │ NO            └─────────────────┘
        ▼
┌─────────────────┐
│ Check           │
│ Documentation   │
│ Again           │
└─────────────────┘
```

## 📱 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ClarityAI Quick Reference                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 🔧 Installation:     pip install -e .                              │
│                                                                     │
│ 🎯 Basic Scoring:    clarity score text.txt --template temp.yaml   │
│                                                                     │
│ 📊 Detailed Score:   clarity score text.txt --template temp.yaml   │
│                      --detailed                                     │
│                                                                     │
│ 🌐 Web Interface:    streamlit run app.py                          │
│                                                                     │
│ 📝 New Template:     clarity create-template --name "my-template"  │
│                      --output my-template.yaml                     │
│                                                                     │
│ 🤖 Training:         clarity train --model microsoft/DialoGPT-small│
│                      --template temp.yaml --steps 20               │
│                                                                     │
│ 🆘 Help:             clarity --help                                │
│                      clarity [command] --help                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Visual Learning Note**: These diagrams and flowcharts are designed to complement the text-based instructions. Use them together for the best understanding of ClarityAI's functionality.