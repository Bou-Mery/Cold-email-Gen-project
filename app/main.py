import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 1.5rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        .main-header h1 {
            color: white;
            font-size: 2.2rem;
            margin: 0;
            font-weight: 700;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .main-header p {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1rem;
            margin-top: 0.5rem;
            position: relative;
            z-index: 1;
            font-weight: 300;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.75rem;
            font-size: 1rem;
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .success-box {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: none;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
        }
        .error-box {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: none;
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="main-header">
            <h1>📧 Cold Mail Generator</h1>
            <p>Generate personalized professional emails in seconds</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ How to use this tool?", expanded=False):
        st.markdown("""
        ### 📋 Instructions
        1. **Copy the URL** of a job posting from a career website
        2. **Paste the URL** in the field below
        3. **Click Generate** to create a personalized email
        4. **Copy and send** the generated email
        
        ---
        
        ### ✨ Features
        - 🎯 Automatic extraction of required skills
        - 🔗 Matching with your portfolio
        - ✍️ Generation of personalized and professional email
        """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🔗 Job Posting URL")
        url_input = st.text_input(
            label="URL",
            value="https://careers.nike.com/fr/dc-processing-athlete-pm-shift/job/R-67062",
            placeholder="https://example.com/job-posting",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### 🚀 Action")
        submit_button = st.button("✨ Generate Email", use_container_width=True)
    
    if submit_button:
        if not url_input or not url_input.startswith("http"):
            st.markdown("""
                <div class="error-box">
                    <strong>⚠️ Error:</strong> Please enter a valid URL starting with http:// or https://
                </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("🔄 Analyzing job posting..."):
                try:
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                    
                    portfolio.load_portfolio()
                    
                    job = llm.extract_jobs(data)
                    
                    if job:
                        with st.spinner("✍️ Generating personalized email..."):
                            skills = job.get('skills', [])
                            links = portfolio.query_links(skills)
                            email = llm.generate_cold_email(job, links)
                        
                        st.markdown("---")
                        st.markdown("### ✉️ Generated Email")
                        st.markdown("""
                            <div class="success-box">
                                <p style="margin: 0 0 1rem 0;"><strong>✅ Email generated successfully!</strong></p>
                                <p style="margin: 0; color: #155724;">You can now copy the email below and use it.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.code(email, language='markdown')
                        
                    else:
                        st.markdown("""
                            <div class="error-box">
                                <strong>⚠️ Warning:</strong> No job posting could be extracted from this URL.
                            </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f"""
                        <div class="error-box">
                            <strong>❌ Error:</strong> {str(e)}
                        </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 2rem 0;">
            <p>Powered by LangChain and Streamlit 🚀</p>
            <p style="font-size: 0.9rem;">Generate professional emails in seconds</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="📧",
        initial_sidebar_state="collapsed"
    )
    create_streamlit_app(chain, portfolio, clean_text)