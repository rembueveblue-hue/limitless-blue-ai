import streamlit as st
from pypdf import PdfReader
import docx2txt
import re

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b111e; color: #ffffff; }
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; }
    .metric-box { padding: 12px; background-color: #162238; border-radius: 6px; margin: 8px 0; border-left: 4px solid #4e8cff; }
    .risk-box { padding: 12px; background-color: #2b161d; border-radius: 6px; margin: 8px 0; border-left: 4px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# 2. Corporate Header
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Instantly parse corporate data into high-priority executive summaries—completely secure & subscription-free.")
st.markdown("---")

# 3. File Uploader Area
uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

# 4. Document Processing Core
if uploaded_file is not None:
    text_content = ""
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    try:
        # Extract raw text locally based on file type
        if file_type == "pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += page.extract_text() or ""
        elif file_type == "docx":
            text_content = docx2txt.process(uploaded_file)
        elif file_type == "txt":
            text_content = uploaded_file.read().decode("utf-8")
            
        st.success(f"📂 Successfully analyzed: {uploaded_file.name}")
        
        # --- LOCAL INTELLIGENCE PROCESSING ---
        # Parse sentences for categorization
        sentences = re.split(r'(?<=[.!?])\s+', text_content)
        
        financial_insights = []
        risk_insights = []
        operational_insights = []
        
        # Scan text for critical corporate markers
        for sentence in sentences:
            s_lower = sentence.lower()
            
            # Identify financial items ($ signs, revenue, profits)
            if any(k in s_lower for k in ["$", "revenue", "profit", "expenditure", "cost", "margin", "penalty"]):
                if len(sentence.strip()) > 10:
                    financial_insights.append(sentence.strip())
                    
            # Identify liabilities, risk, compliance and NDA terms
            if any(k in s_lower for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty"]):
                if len(sentence.strip()) > 10:
                    risk_insights.append(sentence.strip())
                    
            # Identify operational steps and directives
            if any(k in s_lower for k in ["protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub"]):
                if len(sentence.strip()) > 10:
                    operational_insights.append(sentence.strip())

        # Clean duplicates from overlapping matches
        financial_insights = list(set(financial_insights))[:6]
        risk_insights = list(set(risk_insights))[:6]
        operational_insights = list(set(operational_insights))[:6]

        # --- GENERATING THE EXECUTIVE INTERFACE ---
        st.subheader("📋 Executive Intelligence Summary")
        
        # Build a downloadable summary text block dynamically
        summary_text = f"EXECUTIVE SUMMARY FOR {uploaded_file.name.upper()}\n"
        summary_text += "="*40 + "\n\n[FINANCIAL PERFORMANCE BUCKETS]\n"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💵 Financial Metrics & Performance")
            if financial_insights:
                for item in financial_insights:
                    st.markdown(f"<div class='metric-box'>📊 {item}</div>", unsafe_allow_html=True)
                    summary_text += f"- {item}\n"
            else:
                st.info("No explicitly isolated financial metrics found.")
                
            st.markdown("#### ⚙️ Strategic & Operational Directives")
            if operational_insights:
                for item in operational_insights:
                    st.markdown(f"<div class='metric-box'>🛠️ {item}</div>", unsafe_allow_html=True)
                    summary_text += f"\n[OPERATIONAL DIRECTIVES]\n- {item}\n"
            else:
                st.info("No distinct operational steps detected.")

        with col2:
            st.markdown("#### ⚠️ Legal Liabilities & Risk Assessment")
            if risk_insights:
                for item in risk_insights:
                    st.markdown(f"<div class='risk-box'>🚨 {item}</div>", unsafe_allow_html=True)
                    summary_text += f"\n[LEGAL & RISK ASSESSMENT]\n- {item}\n"
            else:
                st.info("No critical legal compliance flags or liability values detected.")
        
        st.markdown("---")
        
        # --- DOWNLOAD BUTTON ---
        st.download_button(
            label="📥 Export Free Summary Report (.txt)",
            data=summary_text,
            file_name=f"Summary_{uploaded_file.name.split('.')[0]}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Error parsing file locally: {e}")
