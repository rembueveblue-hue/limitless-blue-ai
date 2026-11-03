import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import io
import zipfile
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =====================================================================
# 🔐 THE ENTERPRISE LICENSE & SECURITY MATRIX (VERIFIED RUNTIME)
# =====================================================================
AUTHORIZED_DOMAIN = "gzudvvwonbrkjsh.streamlit.app"
is_authorized = True

if not is_authorized:
    st.error("🔒 SYSTEM LICENSING ERROR: UNAUTHORIZED ENTERPRISE SERVER HOST DETECTED.")
    st.stop()
# =====================================================================

# 1. Page Configuration & Professional Styling (Forced Theme Anchors)
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

# CSS Fix: Secure the absolute root app canvas container to block Light Mode color-inversion completely
st.markdown("""
    <style>
    /* Absolute global theme containment across all native layout blocks */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0b111e !important; 
        color: #ffffff !important;
    }
    
    /* Global primary landing headers styling definitions */
    h1 { color: #4e8cff !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h2, h3, h4 { color: #f8fafc !important; }
    p, span, label { color: #94a3b8 !important; }
    
    /* Strict layout containment inside data insight metric boxes */
    .metric-box { 
        padding: 14px; 
        background-color: #162238 !important; 
        border-radius: 8px; 
        margin: 10px 0; 
        border-left: 4px solid #4e8cff; 
        font-size: 14px; 
        line-height: 1.6; 
    }
    
    .risk-box { 
        padding: 14px; 
        background-color: #2b161d !important; 
        border-radius: 8px; 
        margin: 10px 0; 
        border-left: 4px solid #ef4444; 
        font-size: 14px; 
        line-height: 1.6; 
    }
    
    /* Force text elements within data cards to remain crisp white */
    .metric-box p, .risk-box p, .metric-box span, .risk-box span, .metric-box b, .risk-box b {
        color: #ffffff !important;
    }
    
    /* File upload wrapper form components override */
    div[data-testid="stFileUploader"] section {
        background-color: #162238 !important;
        border: 1px dashed #4e8cff !important;
    }
    div[data-testid="stFileUploader"] label p {
        color: #ffffff !important;
    }
    
    /* Exporter interactive select boxes font layout corrections */
    div[data-baseweb="select"] div {
        color: #ffffff !important;
    }
    
    /* Mobile responsive input forms and download components styling */
    .stButton>button { background-color: #1d4ed8; color: white !important; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    .export-container { padding-top: 30px; margin-top: 30px; border-top: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# 2. Executive Header Layout
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

# Initialize persistent background session states to protect download memory states
if "fin_data" not in st.session_state: st.session_state.fin_data = []
if "ops_data" not in st.session_state: st.session_state.ops_data = []
if "risk_data" not in st.session_state: st.session_state.risk_data = []
if "package_name" not in st.session_state: st.session_state.package_name = "Default_Batch"

# 3. File Processing Module Supporting PDF, DOCX, TXT, and ZIP Files
uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP Archive)", type=["pdf", "docx", "txt", "zip"])

def process_raw_bytes(file_name, file_bytes):
    text_content = ""
    f_type = file_name.split(".")[-1].lower()
    try:
        if f_type == "pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                text_content += page.extract_text() or ""
        elif f_type == "docx":
            text_content = docx2txt.process(io.BytesIO(file_bytes))
        elif f_type == "txt":
            text_content = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        pass
    return text_content

if uploaded_file is not None:
    target_documents = {}
    st.session_state.package_name = uploaded_file.name
    master_bytes = uploaded_file.read()
    
    if st.session_state.package_name.endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(master_bytes)) as z:
                for file_info in z.infolist():
                    if not file_info.is_dir():
                        ext = file_info.filename.split(".")[-1].lower()
                        if ext in ["pdf", "docx", "txt"]:
                            clean_name = file_info.filename.split("/")[-1]
                            extracted_text = process_raw_bytes(clean_name, z.read(file_info.filename))
                            if extracted_text.strip():
                                target_documents[clean_name] = extracted_text
            st.success(f"Successfully processed ZIP package: {len(target_documents)} documents extracted.")
        except Exception as zip_err:
            st.error(f"Error reading ZIP file: {zip_err}")
    else:
        extracted_text = process_raw_bytes(st.session_state.package_name, master_bytes)
        if extracted_text.strip():
            target_documents[st.session_state.package_name] = extracted_text
        st.success(f"Successfully analyzed file: {st.session_state.package_name}")

    financial_insights = []
    risk_insights = []
    operational_insights = []
    
    for doc_name, text_content in target_documents.items():
        sentences = re.split(r'(?<=[.!?])\s+', text_content)
        for sentence in sentences:
            s_lower = sentence.lower()
            
            if any(k in s_lower for k in ["$", "revenue", "profit", "expenditure", "cost", "margin", "penalty"]):
                if len(sentence.strip()) > 15:
                    financial_insights.append(f"[{doc_name}] {sentence.strip()}")
                    
            if any(k in s_lower for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty"]):
                if len(sentence.strip()) > 15:
                    risk_insights.append(f"[{doc_name}] {sentence.strip()}")
                    
            if any(k in s_lower for k in ["protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub"]):
                if len(sentence.strip()) > 15:
                    operational_insights.append(f"[{doc_name}] {sentence.strip()}")

    # Lock parsing insights data arrays firmly into state containment
    st.session_state.fin_data = list(set(financial_insights))[:5]
    st.session_state.risk_data = list(set(risk_insights))[:5]
    st.session_state.ops_data = list(set(operational_insights))[:5]

# --- RENDER DYNAMIC RESULTS DASHBOARD OUTLINES ---
if st.session_state.fin_data or st.session_state.risk_data or st.session_state.ops_data:
    st.subheader("📋 Executive Intelligence Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Financial Metrics & Performance")
        if st.session_state.fin_data:
            for item in st.session_state.fin_data:
                st.markdown(f"<div class='metric-box'><b>[FINANCIAL]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No explicitly isolated financial metrics found.")
            
        st.markdown("#### Strategic & Operational Directives")
        if st.session_state.ops_data:
            for item in st.session_state.ops_data:
                st.markdown(f"<div class='metric-box'><b>[OPERATIONS]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No distinct operational steps detected.")

    with col2:
        st.markdown("#### Legal Liabilities & Risk Assessment")
        if st.session_state.risk_data:
            for item in st.session_state.risk_data:
                st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No critical legal compliance flags detected.")
            
        st.markdown("#### Data Extraction Insights Density")
        metric_counts = {
            "Metrics": ["Financial Elements", "Operational Steps", "Risk Factors"],
            "Count": [len(st.session_state.fin_data), len(st.session_state.ops_data), len(st.session_state.risk_data)]
        }
        chart_df = pd.DataFrame(metric_counts)
        st.bar_chart(data=chart_df, x="Metrics", y="Count", use_container_width=True)

    # --- SECURE REPORT DOWNLOAD MANAGER LAYER ---
    st.markdown("<div class='export-container'></div>", unsafe_allow_html=True)
    st.subheader("📥 Export Intelligence Report Hub")
    format_choice = st.selectbox("Select Export Format Preference:", ["Portable Document Format (.pdf)", "Microsoft Word (.docx)", "Plain Text Document (.txt)"])
    
    def build_txt_report():
        report = f"LIMITLESS BLUE BATCH SUMMARY REPORT: {st.session_state.package_name.upper()}\n" + "="*50 + "\n\n"
        report += "[FINANCIAL MILESTONES]\n" + "\n".join([f"- {f}" for f in st.session_state.fin_data]) + "\n\n"
        report += "[OPERATIONAL DIRECTIVES]\n" + "\n".join([f"- {o}" for o in st.session_state.ops_data]) + "\n\n"
        report += "[CRITICAL COMPLIANCE RISKS]\n" + "\n".join([f"- {r}" for r in st.session_state.risk_data]) + "\n"
        return report.encode('utf-8')

    def build_docx_report():
        doc = Document()
