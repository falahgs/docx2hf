import streamlit as st
from docx import Document
import datetime
import json
import io
from datasets import DatasetDict, Dataset
from huggingface_hub import login

# Header styling
st.set_page_config(
    page_title="DOCX to HuggingFace Dataset Converter",
    page_icon="🔄",  # Document conversion icon
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    },
    initial_sidebar_state="expanded"
)

# Hide Streamlit elements and add custom styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Professional color theme */
        :root {
            --primary-color: #2E4057;
            --secondary-color: #4F7CAC;
            --accent-color: #66A6D1;
            --background-color: #F5F7FA;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--primary-color);
        }
        .sidebar .sidebar-content {
            background-color: var(--primary-color);
        }
        
        /* Logo styling */
        .logo-container {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: var(--primary-color);
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .logo-text {
            color: white;
            margin-left: 10px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .logo-icon {
            font-size: 2em;
            margin-right: 10px;
        }
        
        /* Header styling update */
        .main-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .main-header h1, .main-header p {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo in sidebar
st.sidebar.markdown("""
    <div class='logo-container'>
        <span class='logo-icon'>🔄</span>
        <span class='logo-text'>DOCX2HF</span>
    </div>
""", unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    hf_token = st.text_input("Enter your Hugging Face Token:", type="password")
    if hf_token:
        login(token=hf_token)
        st.success("✓ Authenticated")
    
    st.header("Dataset Settings")
    repo_name = st.text_input("Repository Name:", "Falah/rag")
    test_split = st.slider("Test Split %", 10, 50, 20)

# Header
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 1rem;
            background-color: #f0f2f6;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
    </style>
    <div class="main-header">
        <h1>DOCX to HuggingFace Dataset Converter</h1>
        <p>Convert Word documents to JSONL format and upload directly to HuggingFace</p>
    </div>
    """, unsafe_allow_html=True)

# Documentation Section
st.header("📚 Documentation")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Features & Use Cases", "User Guide", "Best Practices"])

with tab1:
    st.markdown("""
    ### About This Tool
    This application helps researchers and data scientists prepare datasets for Large Language Models (LLM) 
    and Natural Language Processing (NLP) tasks by converting DOCX documents into a structured format 
    suitable for training and fine-tuning.
    
    ### What It Does
    - Converts DOCX files to JSONL format
    - Automatically splits data into train/test sets
    - Uploads directly to HuggingFace Hub
    - Handles multiple documents simultaneously
    """)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔑 Key Features
        - **Automatic Train-Test Split**
          - Configurable ratio
          - Balanced distribution
        
        - **HuggingFace Integration**
          - Direct upload to Hub
          - Seamless with transformers
        
        - **Batch Processing**
          - Multiple files at once
          - Efficient processing
        
        - **Structured Output**
          - Consistent JSONL format
          - Clean data structure
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Use Cases
        
        **RAG Systems**
        - Knowledge base creation
        - QA model context prep
        - Document retrieval datasets
        
        **LLM Fine-tuning**
        - Custom training data
        - Domain-specific datasets
        - Evaluation sets
        """)

with tab3:
    st.markdown("""
    ### 📝 Step-by-Step Guide
    
    **1. Authentication**
    - Get your token from [HuggingFace Settings](https://huggingface.co/settings/tokens)
    - Enter it in the sidebar
    
    **2. Configuration**
    - Set repository name (username/repository)
    - Adjust test split percentage
    
    **3. Upload & Process**
    - Select DOCX files
    - Click Generate & Upload
    - Monitor progress
    
    **4. Dataset Format**
    ```json
    {
      "section_title": "RAG Post",
      "content": "Your document content here"
    }
    ```
    """)

with tab4:
    st.markdown("""
    ### 💡 Best Practices
    
    **Document Preparation**
    - Use well-formatted DOCX files
    - Ensure clean, consistent formatting
    - Remove unnecessary headers/footers
    
    **Content Quality**
    - Verify content relevance for NLP/LLM tasks
    - Check for proper text encoding
    - Remove sensitive information
    
    **Dataset Configuration**
    - Choose appropriate train/test split
    - Use descriptive repository names
    - Monitor dataset size and balance
    
    **Processing**
    - Start with small test batches
    - Verify output format
    - Check HuggingFace space usage
    """)

st.markdown("---")

# Streamlit UI for file upload
st.title("Upload DOCX Files to Hugging Face Dataset")
st.subheader("Convert DOCX to JSONL and Upload to Hugging Face")

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(io.BytesIO(docx_file.read()))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# Function to create JSONL from uploaded files
def create_jsonl_data(file_objects):
    train_data, test_data = [], []
    for i, uploaded_file in enumerate(file_objects):
        if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            content = extract_text_from_docx(uploaded_file)
            document = {"section_title": "RAG Post", "content": content}
            if i % (100/test_split) == 0:  # Use slider value for split
                test_data.append(document)
            else:
                train_data.append(document)
        else:
            st.warning(f"File type {uploaded_file.type} not supported!")
    return train_data, test_data

# Upload section
uploaded_files = st.file_uploader("Choose DOCX files", accept_multiple_files=True, type=["docx"])
if uploaded_files:
    st.write(f"Files uploaded: {[file.name for file in uploaded_files]}")
    
    if st.button("Generate JSONL and Upload"):
        train_data, test_data = create_jsonl_data(uploaded_files)
        if train_data or test_data:
            dataset_dict = DatasetDict({
                "train": Dataset.from_list(train_data),
                "test": Dataset.from_list(test_data)
            })
            dataset_dict.push_to_hub(repo_name)
            st.success("Dataset uploaded to Hugging Face successfully with train and test splits!")
        else:
            st.error("No valid files to process.")

# Footer
st.markdown("---")

# Social Links
st.markdown("""
<div style='text-align: center; margin-bottom: 1rem;'>
    <a href='https://x.com/FalahGatea' target='_blank' style='text-decoration: none; color: #1DA1F2; margin: 0 10px;'>Twitter</a>
    <a href='https://www.linkedin.com/in/falah-gatea-060a211a7/' target='_blank' style='text-decoration: none; color: #0077B5; margin: 0 10px;'>LinkedIn</a>
    <a href='https://github.com/falahgs' target='_blank' style='text-decoration: none; color: #333; margin: 0 10px;'>GitHub</a>
    <a href='https://www.instagram.com/falah.g.saleih/' target='_blank' style='text-decoration: none; color: #E4405F; margin: 0 10px;'>Instagram</a>
    <a href='https://www.facebook.com/falahgs' target='_blank' style='text-decoration: none; color: #1877F2; margin: 0 10px;'>Facebook</a>
    <a href='https://iraqprogrammer.wordpress.com/' target='_blank' style='text-decoration: none; color: #21759B; margin: 0 10px;'>Blog</a>
</div>
<div style='text-align: center; margin-bottom: 1rem;'>
    <a href='https://medium.com/@falahgs' target='_blank' style='text-decoration: none; color: #000000; margin: 0 10px;'>Medium</a>
    <a href='https://pypi.org/user/falahgs/' target='_blank' style='text-decoration: none; color: #3775A9; margin: 0 10px;'>PyPI</a>
    <a href='https://www.youtube.com/@FalahgsGate' target='_blank' style='text-decoration: none; color: #FF0000; margin: 0 10px;'>YouTube</a>
    <a href='https://www.amazon.com/stores/Falah-Gatea-Salieh/author/B0BYHXLP7R' target='_blank' style='text-decoration: none; color: #FF9900; margin: 0 10px;'>Amazon</a>
    <a href='https://huggingface.co/Falah' target='_blank' style='text-decoration: none; color: #FFD21E; margin: 0 10px;'>HuggingFace</a>
    <a href='https://www.kaggle.com/falahgatea' target='_blank' style='text-decoration: none; color: #20BEFF; margin: 0 10px;'>Kaggle</a>
    <a href='https://civitai.com/user/falahgs' target='_blank' style='text-decoration: none; color: #4A90E2; margin: 0 10px;'>CivitAI</a>
</div>
""", unsafe_allow_html=True)

# Copyright
st.markdown(f"""
<div style='text-align: center; color: grey; padding: 1rem;'>
    <p>© {datetime.datetime.now().year} DOCX to HuggingFace Dataset Converter v1.0.0</p>
    <p>Copyright © Falah.G.Salieh 2025</p>
</div>
""", unsafe_allow_html=True)
