import streamlit as st
import requests
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Dataset Q&A Bot",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    
    .stButton > button {
        background-color: black;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: #333;
    }
    
    .upload-box {
        border: 2px dashed #ccc;
        padding: 2rem;
        text-align: center;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Dataset Q&A Bot")
st.markdown("Upload your dataset and ask questions in natural language")

uploaded_file = st.file_uploader("Choose a CSV or SQLite file", type=['csv', 'sqlite', 'db'])

if uploaded_file:
    # Show file info
    st.write(f"File uploaded: **{uploaded_file.name}**")
    
    # Question input
    question = st.text_input(
        "Ask a question about your data",
        placeholder="e.g., What was the average age of passengers who survived?"
    )
    
    if st.button("Ask Question", type="primary"):
        if not question:
            st.error("Please enter a question")
        else:
            try:
                # Show loading state
                with st.spinner("Analyzing your question..."):
                    # Prepare the files and data
                    files = {
                        'file': (uploaded_file.name, uploaded_file, 'application/octet-stream')
                    }
                    data = {'question': question}
                    
                    # Make request to FastAPI backend
                    response = requests.post(
                        'http://localhost:8000/ask',
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display answer in a nice box
                        st.markdown("### Answer")
                        answer_box = st.container()
                        with answer_box:
                            if isinstance(result['answer'], dict):
                                # Handle dictionary answers (like comparisons)
                                for key, value in result['answer'].items():
                                    if isinstance(value, float):
                                        st.metric(key, f"{value:.2f}")
                                    else:
                                        st.metric(key, value)
                            else:
                                # Handle simple answers
                                st.markdown(f"**{result['answer']}**")
                            
                            # Show explanation
                            if result.get('explanation'):
                                st.markdown("---")
                                st.markdown("*" + result['explanation'] + "*")
                        
                        # Show dataset info
                        if result.get('dataset_info'):
                            st.markdown("---")
                            info = result['dataset_info']
                            st.markdown(f"Dataset: {info['rows']} rows, {info['columns']} columns")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"Error connecting to the backend server: {str(e)}")
else:
    # Show example questions when no file is uploaded
    st.markdown("### Example Questions")
    st.markdown("""
    - What was the average age of passengers who survived?
    - How many passengers were in first class?
    - Which gender had a higher survival rate?
    - What percentage of passengers survived?
    """)
    
# Footer
st.markdown("---")
st.markdown("Powered by Gemini AI • Built with Streamlit")