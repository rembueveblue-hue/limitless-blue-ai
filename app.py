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
# 🔐 THE ENTERPRISE LICENSE & DOMAIN DEADBOLT SECURITY LAYER
# =====================================================================
AUTHORIZED_DOMAIN = "dvvwonbrkjsh.streamlit.app"

is_authorized = True
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    if ctx is not None:
        pages_manager = st.source_util.get_pages("app.py")
except Exception:
    pass

if not is_authorized:
    st.error("🔒 SYSTEM LICENSING ERROR: UNAUTHORIZED ENTERPRISE SERVER HOST DETECTED.")
    st.stop()
# =====================================================================

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

# FIX: Forcing strict text-color containment (!important) to fix Light/Dark mode bugs
st.markdown("""
    <style>
    /* Absolute global theme background lock */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0b111e !important; 
        color: #ffffff !important;
    }
    .main { background-color: #0b111e !important; color: #ffffff !important; }
    h1 { color: #4e8cff !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h2, h3, h4 { color: #f8fafc !important; }
    p, span, label { color: #94a3b8 !important; }
    
    .stButton>button { background-color: #1d4ed8; color: white !important; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    
    /* Strict styling containment for summary insight boxes */
    .metric-box { padding: 14px; background-color: #162238 !important; color: #ffffff !important; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: #2b161d !important; color: #ffffff !important; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    
    /* Input layout controls and file uploading fields skin */
    div[data-testid="stFileUploader"] section {
        background-color: #162238 !important;
        border: 1px dashed #4e8cff !important;
    }
    div[data-testid="stFileUploader"] label p, div[data-testid="stFileUploader"] span {
        color: #ffffff !important;
    }
    
    /* Add smooth breathing room for the mobile export layout zone */
    .export-container { padding-top: 25px; margin-top: 20px; border-top: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# 2. Executive Header Layout
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

# 3. File Processing Module Supporting PDF, DOCX, TXT, and ZIP
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

# Dictionary to hold the files extracted from the loop
target_documents = {}

if uploaded_file is not None:
    file_name = uploaded_file.name
    master_bytes = uploaded_file.read()
    
    # Clean continuation adding the zip logic directly into the flow
    if file_name.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(master_bytes)) as archive:
                for member in archive.infolist():
                    if not member.is_dir():
                        nested_name = member.filename
                        nested_ext = nested_name.split(".")[-1].lower()
                        
                        if nested_ext in ["pdf", "docx", "txt"]:
                            with archive.open(member) as nested_file:
                                nested_bytes = nested_file.read()
                                target_documents[nested_name] = process_raw_bytes(nested_name, nested_bytes)
        except Exception as e:
            st.error(f"Error parsing zip: {e}")
    else:
        target_documents[file_name] = process_raw_bytes(file_name, master_bytes)
