"""
ClarityAI Training Monitor - Real-time training dashboard
Shows training progress, metrics, and model evaluation
"""
import streamlit as st
import json
import yaml
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Add clarity-ai to path
sys.path.append('/Users/coreyalejandro/Repos/clarity-ai')
from clarity.scorer import Template

def load_training_state(model_dir):
    """Load training state from checkpoint"""
    state_file = os.path.join(model_dir, "trainer_state.json")
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            return json.load(f)
    return None

def load_training_ledger():
    """Load old training runs from ledger"""
    ledger_file = "runs/training_ledger.yaml"
    if os.path.exists(ledger_file):
        with open(ledger_file, 'r') as f:
            return yaml.safe_load(f)
    return {'runs': []}

def test_model_quick(model_path, template_path):
    """Quick test of a model"""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        template = Template.from_yaml(template_path)
        
        test_prompt = "Write a helpful guide:"
        inputs = tokenizer.encode(test_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        score = template.evaluate(generated_text.strip())
        
        return {
            'generated': generated_text.strip(),
            'score': score,
            'status': 'success'
        }
    except Exception as e:
        return {
            'error': str(e),
            'status': 'error'
        }

def main():
    st.set_page_config(
        page_title="ClarityAI Training Monitor",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 ClarityAI Training Monitor")
    st.sidebar.title("Navigation")
    
    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a page", [
        "📊 Training Overview",
        "📈 Training Metrics", 
        "🧪 Model Testing",
        "🔄 Training History",
        "⚙️ Start New Training"
    ])
    
    if page == "📊 Training Overview":
        show_overview()
    elif page == "📈 Training Metrics":
        show_metrics()
    elif page == "🧪 Model Testing":
        show_testing()
    elif page == "🔄 Training History":
        show_history()
    elif page == "⚙️ Start New Training":
        show_training_interface()

def show_overview():
    st.header("📊 Training Overview")
    
    # Check for trained models
    models = []
    if os.path.exists("trained_model"):
        models.append(("trained_model", "Latest Trained Model"))
    if os.path.exists("runs"):
        for item in os.listdir("runs"):
            if os.path.isdir(os.path.join("runs", item)) and item.startswith("run_"):
                models.append((f"runs/{item}/final", f"Run {item}"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🤖 Available Models", len(models))
    
    with col2:
        st.metric("📁 Training Data", len(load_training_data()))
        
    with col3:
        if os.path.exists("trained_model/trainer_state.json"):
            state = load_training_state("trained_model")
            if state and state.get('log_history'):
                final_loss = state['log_history'][-1]['loss']
                st.metric("📉 Final Loss", f"{final_loss:.3f}")
            else:
                st.metric("📉 Final Loss", "N/A")
        else:
            st.metric("📉 Final Loss", "No training yet")
    
    # Show model comparison if available
    st.subheader("🔍 Model Performance Comparison")
    
    if os.path.exists("trained_model"):
        original_result = test_model_quick("microsoft/DialoGPT-small", "templates/demo.yaml")
        trained_result = test_model_quick("trained_model", "templates/demo.yaml")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original Model:**")
            if original_result['status'] == 'success':
                st.write(f"Generated: '{original_result['generated']}'")
                st.write(f"ClarityAI Score: {original_result['score']:.3f}")
            else:
                st.error(f"Error: {original_result['error']}")
        
        with col2:
            st.write("**Trained Model:**")
            if trained_result['status'] == 'success':
                st.write(f"Generated: '{trained_result['generated']}'")
                st.write(f"ClarityAI Score: {trained_result['score']:.3f}")
                
                # Show improvement
                if original_result['status'] == 'success':
                    improvement = trained_result['score'] - original_result['score']
                    if improvement > 0:
                        st.success(f"Improvement: +{improvement:.3f}")
                    elif improvement < 0:
                        st.warning(f"Decline: {improvement:.3f}")
                    else:
                        st.info("No change")
            else:
                st.error(f"Error: {trained_result['error']}")
    else:
        st.info("No trained models available yet. Start training to see comparisons!")

def show_metrics():
    st.header("📈 Training Metrics")
    
    # Load training state
    if os.path.exists("trained_model/trainer_state.json"):
        state = load_training_state("trained_model")
        
        if state and state.get('log_history'):
            # Convert to DataFrame
            df = pd.DataFrame(state['log_history'])
            
            # Loss chart
            fig_loss = px.line(df, x='step', y='loss', 
                             title='Training Loss Over Time',
                             labels={'step': 'Training Step', 'loss': 'Loss'})
            fig_loss.update_layout(height=400)
            st.plotly_chart(fig_loss, use_container_width=True)
            
            # Learning rate chart
            if 'learning_rate' in df.columns:
                fig_lr = px.line(df, x='step', y='learning_rate',
                               title='Learning Rate Schedule',
                               labels={'step': 'Training Step', 'learning_rate': 'Learning Rate'})
                fig_lr.update_layout(height=400)
                st.plotly_chart(fig_lr, use_container_width=True)
            
            # Gradient norm chart
            if 'grad_norm' in df.columns:
                fig_grad = px.line(df, x='step', y='grad_norm',
                                 title='Gradient Norm Over Time',
                                 labels={'step': 'Training Step', 'grad_norm': 'Gradient Norm'})
                fig_grad.update_layout(height=400)
                st.plotly_chart(fig_grad, use_container_width=True)
            
            # Show raw data
            st.subheader("📋 Raw Training Data")
            st.dataframe(df)
            
        else:
            st.warning("No training metrics available")
    else:
        st.info("No training completed yet")

def show_testing():
    st.header("🧪 Model Testing")
    
    # Model selection
    available_models = ["microsoft/DialoGPT-small"]
    if os.path.exists("trained_model"):
        available_models.append("trained_model")
    
    model_path = st.selectbox("Select model to test:", available_models)
    
    # Template selection
    templates = []
    if os.path.exists("templates"):
        templates = [f for f in os.listdir("templates") if f.endswith(".yaml")]
    
    if templates:
        template_file = st.selectbox("Select template:", templates)
        template_path = f"templates/{template_file}"
        
        # Custom prompt
        prompt = st.text_input("Enter test prompt:", "Write a helpful guide:")
        
        if st.button("🧪 Test Model"):
            with st.spinner("Testing model..."):
                try:
                    tokenizer = AutoTokenizer.from_pretrained(model_path)
                    model = AutoModelForCausalLM.from_pretrained(model_path)
                    template = Template.from_yaml(template_path)
                    
                    inputs = tokenizer.encode(prompt, return_tensors="pt")
                    
                    with torch.no_grad():
                        outputs = model.generate(
                            inputs,
                            max_new_tokens=50,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=tokenizer.pad_token_id,
                            eos_token_id=tokenizer.eos_token_id,
                        )
                    
                    generated_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
                    score = template.evaluate(generated_text.strip())
                    
                    st.success("✅ Testing Complete!")
                    st.write(f"**Prompt:** {prompt}")
                    st.write(f"**Generated:** {generated_text.strip()}")
                    st.write(f"**ClarityAI Score:** {score:.3f}")
                    
                    # Show score breakdown
                    detailed_result = template.evaluate_detailed(generated_text.strip())
                    st.subheader("📊 Score Breakdown")
                    for rule in detailed_result['rule_scores']:
                        st.write(f"- **{rule['rule_type']}**: {rule['score']:.3f} (weight: {rule['weight']})")
                    
                except Exception as e:
                    st.error(f"Error testing model: {e}")
    else:
        st.warning("No templates found in templates/ directory")

def show_history():
    st.header("🔄 Training History")
    
    # Load training ledger (old fake runs)
    ledger = load_training_ledger()
    
    if ledger['runs']:
        st.subheader("📋 Previous Training Runs")
        
        for run in ledger['runs']:
            with st.expander(f"🏃 {run['run_id']} - {run['status']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Model:** {run['model_name']}")
                    st.write(f"**Template:** {run['template_path']}")
                    st.write(f"**Steps:** {run['total_steps']}")
                    st.write(f"**Start Time:** {run['start_time']}")
                
                with col2:
                    if 'average_reward' in run:
                        st.write(f"**Average Reward:** {run['average_reward']:.3f}")
                    if 'final_reward' in run:
                        st.write(f"**Final Reward:** {run['final_reward']:.3f}")
                    st.write(f"**Status:** {run['status']}")
                
                if 'step_rewards' in run and run['step_rewards']:
                    rewards_df = pd.DataFrame({
                        'step': range(1, len(run['step_rewards']) + 1),
                        'reward': run['step_rewards']
                    })
                    fig = px.line(rewards_df, x='step', y='reward', 
                                title=f'Rewards for {run["run_id"]}')
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No training history available")

def show_training_interface():
    st.header("⚙️ Start New Training")
    
    with st.form("training_form"):
        model_name = st.selectbox("Base Model:", [
            "microsoft/DialoGPT-small",
            "gpt2", 
            "microsoft/DialoGPT-medium"
        ])
        
        templates = []
        if os.path.exists("templates"):
            templates = [f for f in os.listdir("templates") if f.endswith(".yaml")]
        
        if templates:
            template_file = st.selectbox("Template:", templates)
            template_path = f"templates/{template_file}"
        else:
            st.error("No templates found!")
            return
        
        num_epochs = st.slider("Number of Epochs:", 1, 10, 3)
        learning_rate = st.select_slider("Learning Rate:", [1e-5, 5e-5, 1e-4, 5e-4], value=5e-5)
        output_dir = st.text_input("Output Directory:", "trained_model_new")
        
        submitted = st.form_submit_button("🚀 Start Training")
        
        if submitted:
            st.info("Training would start here...")
            st.code(f"""
# Training command that would run:
python fix_trainer_simple.py \\
    --model_name {model_name} \\
    --template_path {template_path} \\
    --num_epochs {num_epochs} \\
    --learning_rate {learning_rate} \\
    --output_dir {output_dir}
            """)

def load_training_data():
    """Load training data count"""
    try:
        with open('datasets/clarity_training/train.jsonl', 'r') as f:
            return [json.loads(line) for line in f]
    except:
        return []

if __name__ == "__main__":
    main()