---
inclusion: always
---

# ClarityAI Product Overview

ClarityAI is a tool for training Language Learning Models (LLMs) using teacher-style rubrics. The core concept is to allow users to define scoring criteria (rubrics) and use them to evaluate and improve LLM outputs.

## Core Features

- **Rubric-based Scoring Engine**: Define custom scoring rules with weights and parameters
- **Template System**: Create, save, and load scoring templates in YAML format
- **Training Loop**: PPO-based training to improve model outputs based on rubric scores
- **Run Tracking**: Ledger system to track training runs and performance metrics
- **Streamlit UI**: Visual interface for building rubrics and testing scoring

## Key Concepts

- **Rules**: Individual scoring criteria (regex matches, phrase detection, word count, etc.)
- **Templates**: Collections of weighted rules that define a complete scoring rubric
- **Scoring**: Process of evaluating text against templates to produce a score between 0.0 and 1.0
- **Training**: Using scores as rewards to fine-tune language models

## Project Status

ClarityAI is under active development (v0.1.0), with core functionality implemented but still evolving.