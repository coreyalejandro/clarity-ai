import streamlit as st
import yaml
import tempfile
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

from clarity.scorer import Template, score_detailed

# Configure page
st.set_page_config(
    page_title="ClarityAI - Train LLMs with Teacher-Style Rubrics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'scores_history' not in st.session_state:
    st.session_state.scores_history = []
if 'current_template' not in st.session_state:
    st.session_state.current_template = None
if 'sample_texts' not in st.session_state:
    st.session_state.sample_texts = [
        "Python is a helpful programming language for beginners",
        "I don't understand this at all",
        "This is an excellent and clear explanation that provides good guidance",
        "Short text",
        "This comprehensive guide offers detailed insights into machine learning algorithms with practical examples"
    ]

def create_default_template():
    """Create a default template for new users."""
    default_yaml = """name: default_template
description: A sample template for getting started with ClarityAI

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

  - type: regex_match
    weight: 1.0
    params:
      pattern: "[A-Z][a-z]+"
"""
    return default_yaml

def parse_template_yaml(yaml_text):
    """Parse YAML text into a Template object."""
    try:
        data = yaml.safe_load(yaml_text)
        template = Template(data.get('name', 'custom'))
        template.description = data.get('description', '')
        
        for rule_data in data.get('rules', []):
            template.add_rule(
                rule_type=rule_data['type'],
                weight=rule_data.get('weight', 1.0),
                **rule_data.get('params', {})
            )
        
        return template, None
    except Exception as e:
        return None, str(e)

def score_text_with_template(text, template):
    """Score text and return detailed results."""
    try:
        result = template.evaluate_detailed(text)
        return result, None
    except Exception as e:
        return None, str(e)

def create_score_chart(scores_history):
    """Create a plotly chart showing score history."""
    if not scores_history:
        return None
    
    df = pd.DataFrame(scores_history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['score'],
        mode='lines+markers',
        name='Score',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Score History",
        xaxis_title="Evaluation #",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1]),
        height=300,
        showlegend=False
    )
    
    return fig

def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🎯 ClarityAI")
    st.markdown("**Train LLMs with teacher-style rubrics**")
    st.markdown("---")
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Rubric Editor")
        
        # Template management
        st.subheader("Template Management")
        
        template_option = st.radio(
            "Choose template source:",
            ["Use Default Template", "Load from File", "Create Custom"]
        )
        
        yaml_text = ""
        
        if template_option == "Use Default Template":
            yaml_text = create_default_template()
            
        elif template_option == "Load from File":
            uploaded_file = st.file_uploader("Upload YAML template", type=['yaml', 'yml'])
            if uploaded_file:
                yaml_text = uploaded_file.read().decode('utf-8')
            else:
                yaml_text = create_default_template()
                
        elif template_option == "Create Custom":
            yaml_text = st.text_area(
                "Enter YAML template:",
                value=create_default_template(),
                height=200
            )
        
        # YAML editor
        st.subheader("Template Editor")
        edited_yaml = st.text_area(
            "Edit your template:",
            value=yaml_text,
            height=400,
            help="Edit the YAML template to customize scoring rules"
        )
        
        # Parse template
        template, parse_error = parse_template_yaml(edited_yaml)
        
        if parse_error:
            st.error(f"❌ Template Error: {parse_error}")
        else:
            st.success(f"✅ Template '{template.name}' loaded successfully")
            st.session_state.current_template = template
            
            # Show template info
            with st.expander("Template Info"):
                st.write(f"**Name:** {template.name}")
                st.write(f"**Description:** {template.description}")
                st.write(f"**Rules:** {len(template.rules)}")
                
                for i, rule in enumerate(template.rules, 1):
                    st.write(f"{i}. **{rule.rule_type}** (weight: {rule.weight})")
        
        # Download template
        if template:
            st.download_button(
                label="💾 Download Template",
                data=edited_yaml,
                file_name=f"{template.name}.yaml",
                mime="text/yaml"
            )
    
    with col2:
        st.header("🚀 Live Scoring")
        
        if st.session_state.current_template is None:
            st.warning("👈 Please create or load a template first")
            return
        
        # Text input options
        st.subheader("Text Input")
        
        input_option = st.radio(
            "Choose input method:",
            ["Type Custom Text", "Use Sample Texts"]
        )
        
        if input_option == "Type Custom Text":
            input_text = st.text_area(
                "Enter text to score:",
                height=100,
                placeholder="Type your text here..."
            )
        else:
            input_text = st.selectbox(
                "Choose a sample text:",
                st.session_state.sample_texts
            )
            st.text_area("Selected text:", value=input_text, height=100, disabled=True)
        
        # Scoring
        st.subheader("Scoring Results")
        
        if st.button("🎯 Score Text", type="primary"):
            if input_text.strip():
                result, error = score_text_with_template(input_text, st.session_state.current_template)
                
                if error:
                    st.error(f"❌ Scoring Error: {error}")
                else:
                    # Display overall score
                    score_val = result['total_score']
                    st.metric("Overall Score", f"{score_val:.3f}", delta=None)
                    
                    # Add to history
                    st.session_state.scores_history.append({
                        'score': score_val,
                        'text': input_text[:50] + "..." if len(input_text) > 50 else input_text,
                        'timestamp': datetime.now()
                    })
                    
                    # Rule breakdown
                    st.subheader("Rule Breakdown")
                    
                    for rule_score in result['rule_scores']:
                        if 'error' not in rule_score:
                            col_rule, col_weight, col_score = st.columns([2, 1, 1])
                            
                            with col_rule:
                                st.write(f"**{rule_score['rule_type']}**")
                                if rule_score['params']:
                                    st.caption(str(rule_score['params']))
                            
                            with col_weight:
                                st.write(f"Weight: {rule_score['weight']}")
                            
                            with col_score:
                                st.write(f"Score: {rule_score['raw_score']:.3f}")
                        else:
                            st.error(f"❌ {rule_score['rule_type']}: {rule_score['error']}")
            else:
                st.warning("Please enter some text to score")
        
        # Score history chart
        if st.session_state.scores_history:
            st.subheader("Score History")
            
            chart = create_score_chart(st.session_state.scores_history)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            
            # Clear history button
            if st.button("🗑️ Clear History"):
                st.session_state.scores_history = []
                st.rerun()
        
        # Batch scoring
        st.subheader("Batch Scoring")
        
        if st.button("📊 Score All Samples"):
            batch_results = []
            
            for text in st.session_state.sample_texts:
                result, error = score_text_with_template(text, st.session_state.current_template)
                if not error:
                    batch_results.append({
                        'Text': text[:40] + "..." if len(text) > 40 else text,
                        'Score': f"{result['total_score']:.3f}"
                    })
            
            if batch_results:
                df = pd.DataFrame(batch_results)
                st.dataframe(df, use_container_width=True)
    
    # Sidebar with help
    with st.sidebar:
        st.header("📚 Help & Examples")
        
        st.subheader("Rule Types")
        st.write("""
        **contains_phrase**: Checks if text contains specific phrase
        ```yaml
        - type: contains_phrase
          weight: 1.0
          params:
            phrase: "helpful"
        ```
        
        **word_count**: Validates text length
        ```yaml
        - type: word_count
          weight: 1.0
          params:
            min_words: 10
            max_words: 50
        ```
        
        **sentiment_positive**: Detects positive language
        ```yaml
        - type: sentiment_positive
          weight: 1.0
          params: {}
        ```
        
        **regex_match**: Pattern matching
        ```yaml
        - type: regex_match
          weight: 1.0
          params:
            pattern: "[A-Z][a-z]+"
        ```
        
        **cosine_sim**: Word overlap similarity
        ```yaml
        - type: cosine_sim
          weight: 1.0
          params:
            target: "machine learning"
        ```
        """)
        
        st.subheader("Quick Start")
        st.write("""
        1. 📝 Edit the template in the left panel
        2. 🚀 Enter text in the right panel  
        3. 🎯 Click "Score Text" to see results
        4. 📊 View detailed rule breakdown
        5. 📈 Track scores over time
        """)
        
        st.subheader("About ClarityAI")
        st.write("""
        ClarityAI lets you train LLMs the way a teacher grades students:
        - Build scoring rubrics with rules
        - Test on sample texts
        - Use for model training feedback
        """)

if __name__ == "__main__":
    main()