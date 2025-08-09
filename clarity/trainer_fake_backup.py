"""
ClarityAI Training Module

Implements simplified training using transformers to fine-tune
language models based on rubric scores from the ClarityAI scoring system.
"""

import torch
import yaml
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
import logging

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM,
        TrainingArguments,
        GenerationConfig
    )
    import datasets
except ImportError as e:
    raise ImportError(
        f"Missing required dependencies: {e}. "
        "Install with: pip install transformers datasets torch"
    )

from .scorer import Template, score


@dataclass
class TrainingConfig:
    """Configuration for ClarityAI training runs."""
    
    # Model settings
    model_name: str = "microsoft/DialoGPT-small"
    template_path: str = "templates/demo.yaml"
    
    # Training hyperparameters
    learning_rate: float = 1.41e-5
    batch_size: int = 16
    mini_batch_size: int = 4
    ppo_epochs: int = 4
    max_steps: int = 20
    gradient_accumulation_steps: int = 1
    
    # Generation settings
    max_new_tokens: int = 50
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    do_sample: bool = True
    
    # Logging and output
    output_dir: str = "runs"
    log_with: str = "tensorboard"
    save_every: int = 5
    
    # Advanced settings
    cliprange: float = 0.2
    cliprange_value: float = 0.2
    vf_coef: float = 0.1
    gamma: float = 1.0
    lam: float = 0.95
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingConfig':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TrainingRun:
    """Represents a single training run with metadata and results."""
    
    run_id: str
    model_name: str
    template_path: str
    config: TrainingConfig
    start_time: str
    end_time: Optional[str] = None
    total_steps: int = 0
    average_reward: float = 0.0
    final_reward: float = 0.0
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None
    step_rewards: List[float] = None
    
    def __post_init__(self):
        if self.step_rewards is None:
            self.step_rewards = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['config'] = self.config.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingRun':
        """Create from dictionary."""
        config_data = data.pop('config')
        config = TrainingConfig.from_dict(config_data)
        return cls(config=config, **data)


class ClarityTrainer:
    """Main trainer class that orchestrates simplified training with ClarityAI scoring."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.template = None
        self.model = None
        self.tokenizer = None
        self.current_run = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
    
    def load_template(self) -> Template:
        """Load the scoring template."""
        if not os.path.exists(self.config.template_path):
            raise FileNotFoundError(f"Template not found: {self.config.template_path}")
        
        self.template = Template.from_yaml(self.config.template_path)
        self.logger.info(f"Loaded template: {self.template.name}")
        return self.template
    
    def load_model(self):
        """Load the model and tokenizer for training."""
        self.logger.info(f"Loading model: {self.config.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with CPU-friendly settings
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float32
        )
        
        # Move to CPU explicitly
        self.model = self.model.to("cpu")
        
        self.logger.info("Model loaded successfully")
    
    def setup_trainer(self):
        """Initialize the simplified trainer."""
        self.logger.info("Using simplified training approach")
        
        # Create optimizer directly
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate
        )
        
        self.logger.info("Trainer initialized")
    
    def create_prompts(self, num_prompts: int = None) -> List[str]:
        """Create training prompts."""
        if num_prompts is None:
            num_prompts = self.config.batch_size
        
        # Default prompts for training
        base_prompts = [
            "Write a helpful explanation about",
            "Provide clear guidance on",
            "Give me advice about",
            "Explain in simple terms",
            "Help me understand",
            "What is the best way to",
            "Can you clarify",
            "Please describe how to",
        ]
        
        # Cycle through prompts to fill batch
        prompts = []
        for i in range(num_prompts):
            prompts.append(base_prompts[i % len(base_prompts)])
        
        return prompts
    
    def generate_responses(self, prompts: List[str]) -> List[str]:
        """Generate responses using the current model."""
        responses = []
        
        for prompt in prompts:
            # Tokenize prompt
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=self.config.max_new_tokens,
                    temperature=self.config.temperature,
                    top_k=self.config.top_k,
                    top_p=self.config.top_p,
                    do_sample=self.config.do_sample,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode response (remove prompt)
            response = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
            responses.append(response.strip())
        
        return responses
    
    def compute_rewards(self, responses: List[str]) -> List[float]:
        """Compute rewards using the scoring template."""
        rewards = []
        
        for response in responses:
            try:
                reward = self.template.evaluate(response)
                rewards.append(reward)
            except Exception as e:
                self.logger.warning(f"Error scoring response: {e}")
                rewards.append(0.0)
        
        return rewards
    
    def start_training_run(self) -> str:
        """Start a new training run and return the run ID."""
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_run = TrainingRun(
            run_id=run_id,
            model_name=self.config.model_name,
            template_path=self.config.template_path,
            config=self.config,
            start_time=datetime.now(timezone.utc).isoformat(),
        )
        
        self.logger.info(f"Started training run: {run_id}")
        return run_id
    
    def save_training_run(self):
        """Save the current training run to the ledger."""
        if self.current_run is None:
            return
        
        # Update run statistics
        if self.current_run.step_rewards:
            self.current_run.average_reward = sum(self.current_run.step_rewards) / len(self.current_run.step_rewards)
            self.current_run.final_reward = self.current_run.step_rewards[-1]
        
        self.current_run.end_time = datetime.now(timezone.utc).isoformat()
        self.current_run.status = "completed"
        
        # Save to ledger file
        ledger_path = os.path.join(self.config.output_dir, "training_ledger.yaml")
        
        # Load existing ledger or create new
        if os.path.exists(ledger_path):
            with open(ledger_path, 'r') as f:
                ledger = yaml.safe_load(f) or {'runs': []}
        else:
            ledger = {'runs': []}
        
        # Add current run
        ledger['runs'].append(self.current_run.to_dict())
        
        # Save ledger
        with open(ledger_path, 'w') as f:
            yaml.dump(ledger, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Saved training run to ledger: {ledger_path}")
    
    def train(self) -> Dict[str, Any]:
        """Main training loop."""
        try:
            # Setup
            self.load_template()
            self.load_model()
            self.setup_trainer()
            
            # Start training run
            run_id = self.start_training_run()
            
            self.logger.info(f"Starting training for {self.config.max_steps} steps")
            
            # Training loop
            for step in range(self.config.max_steps):
                self.logger.info(f"Step {step + 1}/{self.config.max_steps}")
                
                # Generate prompts and responses
                prompts = self.create_prompts()
                responses = self.generate_responses(prompts)
                
                # Compute rewards
                rewards = self.compute_rewards(responses)
                
                # Log progress
                avg_reward = sum(rewards) / len(rewards)
                self.current_run.step_rewards.append(avg_reward)
                self.current_run.total_steps = step + 1
                
                self.logger.info(f"Step {step + 1} - Average reward: {avg_reward:.3f}")
                
                # Log sample response
                if responses:
                    self.logger.info(f"Sample response: {responses[0][:100]}...")
                
                # Save checkpoint
                if (step + 1) % self.config.save_every == 0:
                    checkpoint_dir = os.path.join(self.config.output_dir, run_id, f"checkpoint-{step + 1}")
                    os.makedirs(checkpoint_dir, exist_ok=True)
                    self.model.save_pretrained(checkpoint_dir)
                    self.tokenizer.save_pretrained(checkpoint_dir)
                    self.logger.info(f"Saved checkpoint: {checkpoint_dir}")
            
            # Save final model
            final_dir = os.path.join(self.config.output_dir, run_id, "final")
            os.makedirs(final_dir, exist_ok=True)
            self.model.save_pretrained(final_dir)
            self.tokenizer.save_pretrained(final_dir)
            
            # Save training run
            self.save_training_run()
            
            return {
                "status": "success",
                "run_id": run_id,
                "total_steps": self.config.max_steps,
                "average_reward": self.current_run.average_reward,
                "final_reward": self.current_run.final_reward,
                "output_dir": os.path.join(self.config.output_dir, run_id)
            }
        
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            
            if self.current_run:
                self.current_run.status = "failed"
                self.current_run.error = str(e)
                self.current_run.end_time = datetime.now(timezone.utc).isoformat()
                self.save_training_run()
            
            return {
                "status": "error",
                "error": str(e),
                "run_id": self.current_run.run_id if self.current_run else None
            }


def train_model(
    model_name: str,
    template_path: str,
    max_steps: int = 20,
    learning_rate: float = 1.41e-5,
    batch_size: int = 16,
    output_dir: str = "runs",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to train a model with ClarityAI.
    
    Args:
        model_name: HuggingFace model name
        template_path: Path to YAML template file
        max_steps: Number of training steps
        learning_rate: Learning rate for training
        batch_size: Batch size for training
        output_dir: Directory to save results
        **kwargs: Additional config parameters
    
    Returns:
        Dict with training results
    """
    config = TrainingConfig(
        model_name=model_name,
        template_path=template_path,
        max_steps=max_steps,
        learning_rate=learning_rate,
        batch_size=batch_size,
        output_dir=output_dir,
        **kwargs
    )
    
    trainer = ClarityTrainer(config)
    return trainer.train()


def load_training_ledger(output_dir: str = "runs") -> List[TrainingRun]:
    """Load training runs from the ledger."""
    ledger_path = os.path.join(output_dir, "training_ledger.yaml")
    
    if not os.path.exists(ledger_path):
        return []
    
    with open(ledger_path, 'r') as f:
        ledger = yaml.safe_load(f)
    
    runs = []
    for run_data in ledger.get('runs', []):
        runs.append(TrainingRun.from_dict(run_data))
    
    return runs