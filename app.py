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
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main { 
        background-color: #0b111e !important; 
        color: #ffffff !important; 
    }
    h1 { color: #4e8cff !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h2, h3, h4 { color: #f8fafc !important; }
    p, span, label { color: #94a3b8 !important; }
    .stButton>button { background-color: #1d4ed8; color: white !important; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    
    /* Strict styling containment for summary insight boxes */
    .metric-box { padding: 14px; background-color: #162238 !important; color: #ffffff !important; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: #2b161d !important; color: #ffffff !important; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    
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

# This will store the text from your uploaded file(s)
extracted_text = ""

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    
    # Check if payload requires archive unpacking
    if file_name.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                for z_info in z.infolist():
                    if not z_info.is_dir():
                        # Read raw nested document bytes out of the zip container
                        nested_bytes = z.read(z_info.filename)
                        # Route the bytes through your working extraction function
                        clean_text = process_raw_bytes(z_info.filename, nested_bytes)
                        # Append it directly to the processing stream
                        extracted_text += clean_text + "\n"
        except Exception as e:
            st.error(f"Error reading zip file: {e}")
    else:
        # Keep original single standalone document extraction route exactly as it was
        extracted_text = process_raw_bytes(file_name, file_bytes)
