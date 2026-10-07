import streamlit as st
import openai
from pypdf import PdfReader
import docx2txt

# 1. Page Configuration & Styling
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b111e; color: #ffffff; }
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Instantly parse corporate and legal data into high-priority executive summaries.")
st.markdown("---")

# 3. Sidebar for API Configuration
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# 4. File Uploader Area
uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

# 5. Document Processing Core
if uploaded_file is not None:
    text_content = ""
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    try:
        if file_type == "pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += page.extract_text() or ""
        elif file_type == "docx":
            text_content = docx2txt.process(uploaded_file)
        elif file_type == "txt":
            text_content = uploaded_file.read().decode("utf-8")
            
        st.success(f"Successfully loaded: {uploaded_file.name}")
        
        # --- FEATURE 1: EXECUTIVE SUMMARY GENERATION ---
        st.subheader("📋 Executive Intelligence Summary")
        
        if not api_key:
            st.warning("Please enter your OpenAI API Key in the sidebar to generate insights.")
        else:
            client = openai.OpenAI(api_key=api_key)
            
            # Simple caching so it doesn't re-run the API on every click
            if "summary" not in st.session_state:
                with st.spinner("Analyzing document structure and extracting key entities..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an elite corporate intelligence analyst. Summarize this document focusing on core actions, liabilities, financial metrics, and executive key takeaways. Use clean Markdown formatting."},
                            {"role": "user", "content": f"Document Content:\n\n{text_content[:8000]}"} # Limits tokens safely
                        ]
                    )
                    st.session_state.summary = response.choices[0].message.content
            
            st.markdown(st.session_state.summary)
            
            # --- FEATURE 2: DOWNLOAD BUTTON ---
            st.download_button(
                label="📥 Download Executive Summary (.txt)",
                data=st.session_state.summary,
                file_name=f"Summary_{uploaded_file.name}.txt",
                mime="text/plain"
            )
            
            # --- FEATURE 3: INTERACTIVE DOCUMENT CHAT ---
            st.markdown("---")
            st.subheader("💬 Interactive Intelligence Chat")
            st.caption("Ask specific questions regarding compliance, data points, or contract clauses within this document.")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if user_query := st.chat_input("Ask something about this document..."):
                with st.chat_message("user"):
                    st.markdown(user_query)
                st.session_state.messages.append({"role": "user", "content": user_query})
                
                with st.chat_message("assistant"):
                    with st.spinner("Reviewing document context..."):
                        chat_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": f"You are analyzing this document context:\n\n{text_content[:6000]}\n\nAnswer the user's questions strictly using facts from the document context provided. If not found, synthesize a professional response noting the context limitations."},
                                *st.session_state.messages
                            ]
                        )
                        answer = chat_response.choices[0].message.content
                        st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Error parsing file: {e}")

