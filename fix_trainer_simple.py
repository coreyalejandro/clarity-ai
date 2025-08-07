"""
Simple script to actually fine-tune models using ClarityAI scoring
This replaces the fake training in trainer.py with real training
"""
import torch
import json
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from torch.utils.data import Dataset
import sys
import os

# Add clarity-ai to path
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

class ClarityDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }

def load_training_data(data_path="datasets/clarity_training/train.jsonl"):
    """Load training data from our JSONL file"""
    texts = []
    with open(data_path, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            texts.append(data['text'])
    return texts

def train_model_real(model_name="microsoft/DialoGPT-small", 
                    template_path="templates/demo.yaml",
                    output_dir="./trained_model",
                    num_epochs=3,
                    learning_rate=5e-5,
                    training_data_path="datasets/clarity_training/train.jsonl"):
    """Actually fine-tune a model using real training"""
    
    print("🚀 Starting REAL fine-tuning with ClarityAI...")
    
    # Load model and tokenizer
    print(f"📦 Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Add padding token if missing
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id
    
    # Load training data
    print("📊 Loading training data...")
    texts = load_training_data(training_data_path)
    print(f"Found {len(texts)} training examples")
    
    # Create dataset
    train_dataset = ClarityDataset(texts, tokenizer)
    
    # Setup training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        logging_steps=1,
        save_steps=50,
        save_total_limit=2,
        prediction_loss_only=True,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
    )
    
    # Create data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    # Start training
    print("🔥 Starting training...")
    trainer.train()
    
    # Save the model
    print(f"💾 Saving trained model to {output_dir}")
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    # Test the model with ClarityAI scoring
    print("🧪 Testing trained model...")
    test_model_with_clarity(output_dir, template_path)
    
    return {
        "status": "success",
        "model_path": output_dir,
        "message": "Model trained successfully with REAL fine-tuning!"
    }

def test_model_with_clarity(model_path, template_path):
    """Test the trained model with ClarityAI scoring"""
    
    # Load trained model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    
    # Load ClarityAI template
    template = Template.from_yaml(template_path)
    
    # Test prompts
    test_prompts = [
        "Write a helpful guide:",
        "Create useful content:",
        "Provide clear information:"
    ]
    
    print("\n" + "="*50)
    print("🎯 TESTING TRAINED MODEL WITH CLARITYAI SCORING")
    print("="*50)
    
    for prompt in test_prompts:
        # Generate text
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        # Decode generated text
        generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        
        # Score with ClarityAI
        clarity_score = template.evaluate(generated_text.strip())
        
        print(f"\n🔤 Prompt: {prompt}")
        print(f"📝 Generated: {generated_text.strip()}")
        print(f"⭐ ClarityAI Score: {clarity_score:.3f}")
    
    print("\n" + "="*50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    result = train_model_real()
    print(f"\n🎉 Final result: {result}")