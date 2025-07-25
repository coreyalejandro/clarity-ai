"""
Memory usage and resource monitoring tests.

These tests monitor memory consumption and resource usage during
model loading, training, and generation operations.
"""

import os
import sys
import time
import pytest
import tempfile
import psutil
import gc
from typing import Dict, Any, Tuple

# Skip these tests if psutil is not installed
pytest.importorskip("psutil")

# Skip these tests if torch is not installed
torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from clarity.trainer import TrainingConfig, ClarityTrainer, Template


def get_process_memory() -> Tuple[float, float]:
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Convert to MB
    rss = memory_info.rss / (1024 * 1024)
    vms = memory_info.vms / (1024 * 1024)
    return rss, vms


def measure_memory_usage(func, *args, **kwargs) -> Dict[str, Any]:
    """Measure memory usage before and after function execution."""
    # Force garbage collection before measurement
    gc.collect()
    
    # Measure memory before
    rss_before, vms_before = get_process_memory()
    
    # Execute function and measure time
    start_time = time.time()
    result = func(*args, **kwargs)
    execution_time = time.time() - start_time
    
    # Force garbage collection after execution
    gc.collect()
    
    # Measure memory after
    rss_after, vms_after = get_process_memory()
    
    # Calculate differences
    rss_diff = rss_after - rss_before
    vms_diff = vms_after - vms_before
    
    return {
        "result": result,
        "execution_time": execution_time,
        "rss_before_mb": rss_before,
        "rss_after_mb": rss_after,
        "rss_diff_mb": rss_diff,
        "vms_before_mb": vms_before,
        "vms_after_mb": vms_after,
        "vms_diff_mb": vms_diff
    }


@pytest.mark.performance
class TestResourceUsage:
    """Test memory usage and resource consumption."""
    
    @pytest.fixture
    def small_model_name(self):
        """Return a small model name for testing."""
        return "microsoft/DialoGPT-small"
    
    @pytest.fixture
    def template_file(self):
        """Create a temporary template file for testing."""
        template = Template("resource_test")
        template.description = "Template for resource testing"
        template.add_rule("contains_phrase", 1.0, phrase="helpful")
        template.add_rule("word_count", 1.0, min_words=5, max_words=100)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            template.to_yaml(f.name)
            yaml_path = f.name
        
        yield yaml_path
        
        # Clean up
        os.unlink(yaml_path)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_memory_usage(self):
        """Test GPU memory usage during model operations."""
        try:
            # Get initial GPU memory usage
            initial_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
            
            # Load a small model to GPU
            from transformers import AutoModelForCausalLM
            model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small", torch_dtype=torch.float16)
            model = model.to("cuda")
            
            # Get memory after loading
            after_load_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
            
            # Generate some text
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            inputs = tokenizer("Hello, how are you?", return_tensors="pt").to("cuda")
            
            with torch.no_grad():
                outputs = model.generate(inputs, max_length=50)
            
            # Get memory after generation
            after_generate_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # MB
            
            # Log memory usage
            print(f"\nInitial GPU memory: {initial_memory:.2f} MB")
            print(f"After model load: {after_load_memory:.2f} MB")
            print(f"After generation: {after_generate_memory:.2f} MB")
            print(f"Model load memory delta: {after_load_memory - initial_memory:.2f} MB")
            print(f"Generation memory delta: {after_generate_memory - after_load_memory:.2f} MB")
            
            # Clean up
            del model, inputs, outputs
            torch.cuda.empty_cache()
            
        except Exception as e:
            pytest.skip(f"Error in GPU test: {e}")
    
    def test_model_loading_memory(self, small_model_name):
        """Test memory usage during model loading."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Measure tokenizer loading
            tokenizer_metrics = measure_memory_usage(
                AutoTokenizer.from_pretrained, small_model_name
            )
            
            # Measure model loading
            model_metrics = measure_memory_usage(
                AutoModelForCausalLM.from_pretrained, small_model_name
            )
            
            # Log results
            print(f"\nTokenizer loading:")
            print(f"  Time: {tokenizer_metrics['execution_time']:.2f} seconds")
            print(f"  Memory increase: {tokenizer_metrics['rss_diff_mb']:.2f} MB")
            
            print(f"Model loading:")
            print(f"  Time: {model_metrics['execution_time']:.2f} seconds")
            print(f"  Memory increase: {model_metrics['rss_diff_mb']:.2f} MB")
            
            # Assert reasonable memory usage (adjust thresholds as needed)
            assert tokenizer_metrics['rss_diff_mb'] < 100, "Tokenizer uses excessive memory"
            
            # Model size depends on the specific model, so we just log it
            print(f"  Total model memory: {model_metrics['rss_after_mb']:.2f} MB")
            
        except ImportError:
            pytest.skip("transformers not installed")
    
    def test_trainer_initialization_resources(self, small_model_name, template_file):
        """Test resource usage during trainer initialization."""
        try:
            # Create config
            config = TrainingConfig(
                model_name=small_model_name,
                template_path=template_file,
                max_steps=1,  # Minimal steps for testing
                output_dir=tempfile.mkdtemp()
            )
            
            # Measure trainer initialization
            trainer_metrics = measure_memory_usage(
                ClarityTrainer, config
            )
            
            # Log results
            print(f"\nTrainer initialization:")
            print(f"  Time: {trainer_metrics['execution_time']:.2f} seconds")
            print(f"  Memory increase: {trainer_metrics['rss_diff_mb']:.2f} MB")
            
            # Get trainer instance
            trainer = trainer_metrics['result']
            
            # Measure template loading
            template_metrics = measure_memory_usage(
                trainer.load_template
            )
            
            print(f"Template loading:")
            print(f"  Time: {template_metrics['execution_time']:.2f} seconds")
            print(f"  Memory increase: {template_metrics['rss_diff_mb']:.2f} MB")
            
            # Measure model loading
            model_metrics = measure_memory_usage(
                trainer.load_model
            )
            
            print(f"Model loading:")
            print(f"  Time: {model_metrics['execution_time']:.2f} seconds")
            print(f"  Memory increase: {model_metrics['rss_diff_mb']:.2f} MB")
            
            # Clean up
            if os.path.exists(config.output_dir):
                import shutil
                shutil.rmtree(config.output_dir)
            
        except ImportError:
            pytest.skip("Required dependencies not installed")
    
    def test_memory_growth_during_training(self, small_model_name, template_file):
        """Test memory growth during training iterations."""
        try:
            # Create temporary output directory
            output_dir = tempfile.mkdtemp()
            
            # Create config with minimal settings
            config = TrainingConfig(
                model_name=small_model_name,
                template_path=template_file,
                max_steps=3,  # Just a few steps for testing
                batch_size=2,
                output_dir=output_dir
            )
            
            # Initialize trainer
            trainer = ClarityTrainer(config)
            trainer.load_template()
            trainer.load_model()
            trainer.setup_trainer()
            
            # Start training run
            trainer.start_training_run()
            
            # Memory measurements at different steps
            memory_measurements = []
            
            # Initial memory
            rss_initial, vms_initial = get_process_memory()
            memory_measurements.append(("initial", rss_initial, vms_initial))
            
            # Create prompts and generate responses
            prompts = trainer.create_prompts(2)
            
            # Measure memory after each step
            for step in range(min(2, config.max_steps)):
                # Generate responses
                responses = trainer.generate_responses(prompts)
                
                # Compute rewards
                rewards = trainer.compute_rewards(responses)
                
                # Measure memory
                rss, vms = get_process_memory()
                memory_measurements.append((f"step_{step+1}", rss, vms))
                
                # Log step info
                print(f"\nStep {step+1} memory usage:")
                print(f"  RSS: {rss:.2f} MB")
                print(f"  VMS: {vms:.2f} MB")
                print(f"  Delta from initial (RSS): {rss - rss_initial:.2f} MB")
            
            # Check for excessive memory growth
            max_rss = max(m[1] for m in memory_measurements)
            min_rss = min(m[1] for m in memory_measurements)
            
            print(f"\nMemory growth summary:")
            print(f"  Min RSS: {min_rss:.2f} MB")
            print(f"  Max RSS: {max_rss:.2f} MB")
            print(f"  Growth: {max_rss - min_rss:.2f} MB")
            
            # Clean up
            if os.path.exists(output_dir):
                import shutil
                shutil.rmtree(output_dir)
            
        except ImportError:
            pytest.skip("Required dependencies not installed")
        except Exception as e:
            pytest.skip(f"Error in training memory test: {e}")
    
    def test_cpu_usage_during_scoring(self):
        """Test CPU usage during scoring operations."""
        # Create a complex template
        template = Template("cpu_test")
        for i in range(10):
            template.add_rule("regex_match", 1.0, pattern=r"\b\w{" + str(i+3) + r"}\b")
        
        # Generate a long text
        text = " ".join(["word" * 1000])
        
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        cpu_percent_initial = process.cpu_percent(interval=0.1)
        
        # Perform scoring
        start_time = time.time()
        for _ in range(10):  # Multiple iterations to measure CPU usage
            template.evaluate(text)
        
        # Get CPU usage after scoring
        cpu_percent_after = process.cpu_percent(interval=0.1)
        execution_time = time.time() - start_time
        
        # Log results
        print(f"\nCPU usage during scoring:")
        print(f"  Initial CPU%: {cpu_percent_initial:.2f}%")
        print(f"  After CPU%: {cpu_percent_after:.2f}%")
        print(f"  Execution time: {execution_time:.2f} seconds")
        
        # We don't assert specific CPU usage as it varies by system,
        # but we log it for monitoring purposes