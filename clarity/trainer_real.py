"""
ClarityAI Real Training Module - ACTUALLY trains models using rubric scores
This replaces the fake training with real fine-tuning
"""
from ..fix_trainer_simple import train_model_real

# Export the real training function
train_model = train_model_real