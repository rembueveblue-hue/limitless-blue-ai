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

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b111e; color: #ffffff; }
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h3 { color: #94a3b8; font-weight: 400; }
    h4 { color: #f8fafc; border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    .metric-box { padding: 14px; background-color: #162238; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: #2b161d; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# 2. Executive Header Layout
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

# 3. File Processing Module Supporting PDF, DOCX, TXT, and ZIP Packages
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
    master_name = uploaded_file.name
    master_bytes = uploaded_file.read()
    
    # Process ZIP package or unpack single documents seamlessly
    if master_name.endswith(".zip"):
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
        extracted_text = process_raw_bytes(master_name, master_bytes)
        if extracted_text.strip():
            target_documents[master_name] = extracted_text
        st.success(f"Successfully analyzed file: {master_name}")

    # Process all collected text vectors
    financial_insights = []
    risk_insights = []
    operational_insights = []
    
    for doc_name, text_content in target_documents.items():
        sentences = re.split(r'(?<=[.!?])\s+', text_content)
        for sentence in sentences:
            s_lower = sentence.lower()
            
            # Financial Data Mapping
            if any(k in s_lower for k in ["$", "revenue", "profit", "expenditure", "cost", "margin", "penalty"]):
                if len(sentence.strip()) > 15:
                    financial_insights.append(f"[{doc_name}] {sentence.strip()}")
                    
            # Legal Liabilities Mapping
            if any(k in s_lower for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty"]):
                if len(sentence.strip()) > 15:
                    risk_insights.append(f"[{doc_name}] {sentence.strip()}")
                    
            # Operations Mapping
            if any(k in s_lower for k in ["protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub"]):
                if len(sentence.strip()) > 15:
                    operational_insights.append(f"[{doc_name}] {sentence.strip()}")

    # Deduplicate findings
    financial_insights = list(set(financial_insights))[:5]
    risk_insights = list(set(risk_insights))[:5]
    operational_insights = list(set(operational_insights))[:5]

    # --- DYNAMIC DASHBOARD OUTPUT ---
    st.subheader("📋 Executive Intelligence Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Financial Metrics & Performance")
        if financial_insights:
            for item in financial_insights:
                st.markdown(f"<div class='metric-box'><b>[FINANCIAL]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No explicitly isolated financial metrics found.")
            
        st.markdown("#### Strategic & Operational Directives")
        if operational_insights:
            for item in operational_insights:
                st.markdown(f"<div class='metric-box'><b>[OPERATIONS]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No distinct operational steps detected.")

    with col2:
        st.markdown("#### Legal Liabilities & Risk Assessment")
        if risk_insights:
            for item in risk_insights:
                st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {item}</div>", unsafe_allow_html=True)
        else:
            st.info("No critical legal compliance flags detected.")
            
        # --- DYNAMIC DATA DENSITY CHART ---
        st.markdown("#### Data Extraction Insights Density")
        metric_counts = {
            "Metrics": ["Financial Elements", "Operational Steps", "Risk Factors"],
            "Count": [len(financial_insights), len(operational_insights), len(risk_insights)]
        }
        chart_df = pd.DataFrame(metric_counts)
        st.bar_chart(data=chart_df, x="Metrics", y="Count", use_container_width=True)
    
    st.markdown("---")
    
    # --- SECURE MULTI-FORMAT EXPORT GENERATOR HUB ---
    st.subheader("📥 Export Intelligence Report Hub")
    format_choice = st.selectbox("Select Export Format Preference:", ["Portable Document Format (.pdf)", "Microsoft Word (.docx)", "Plain Text Document (.txt)"])
    
    # Text Document Builder (.txt)
    def build_txt_report():
        report = f"LIMITLESS BLUE BATCH SUMMARY REPORT: {master_name.upper()}\n" + "="*50 + "\n\n"
        report += "[FINANCIAL MILESTONES]\n" + "\n".join([f"- {f}" for f in financial_insights]) + "\n\n"
        report += "[OPERATIONAL DIRECTIVES]\n" + "\n".join([f"- {o}" for o in operational_insights]) + "\n\n"
        report += "[CRITICAL COMPLIANCE RISKS]\n" + "\n".join([f"- {r}" for r in risk_insights]) + "\n"
        return report.encode('utf-8')

    # Microsoft Word Document Builder (.docx)
    def build_docx_report():
        doc = Document()
        doc.add_heading("Limitless Blue AI | Batch Summary Report", 0)
        doc.add_paragraph(f"Source Package: {master_name}")
        
        doc.add_heading("Financial Metrics & Performance Index", level=1)
        for item in financial_insights: doc.add_paragraph(item, style='List Bullet')
        
        doc.add_heading("Strategic & Operational Directives", level=1)
        for item in operational_insights: doc.add_paragraph(item, style='List Bullet')
        
        doc.add_heading("Legal Liabilities & Risk Assessment", level=1)
        for item in risk_insights: doc.add_paragraph(item, style='List Bullet')
        
        output_stream = io.BytesIO()
        doc.save(output_stream)
        return output_stream.getvalue()

    # Streamlined PDF Document Builder (.pdf)
    def build_pdf_report():
        output_stream = io.BytesIO()
        pdf_doc = SimpleDocTemplate(output_stream, pagesize=letter, title="Limitless Blue Batch Review")
        styles = getSampleStyleSheet()
        
        document_content = [
            Paragraph("<font size=22 color='#1d4ed8'><b>🔷 Limitless Blue Executive Report</b></font>", styles['Title']),
            Paragraph(f"<b>Batch Data Processing Summary: {master_name}</b>", styles['Normal']),
            Spacer(1, 15),
            Paragraph("<font size=14 color='#1e3a8a'><b>Financial Metrics & Performance</b></font>", styles['Heading2']),
            Spacer(1, 5)
        ]
        for item in financial_insights:
            document_content.append(Paragraph(f"• {item}", styles['Normal']))
            document_content.append(Spacer(1, 6))
            
        document_content.append(Spacer(1, 10))
        document_content.append(Paragraph("<font size=14 color='#1e3a8a'><b>Strategic & Operational Directives</b></font>", styles['Heading2']))
        document_content.append(Spacer(1, 5))
        for item in operational_insights:
            document_content.append(Paragraph(f"• {item}", styles['Normal']))
            document_content.append(Spacer(1, 6))
            
        document_content.append(Spacer(1, 10))
        document_content.append(Paragraph("<font size=14 color='#7f1d1d'><b>Legal Liabilities & Critical Compliance Risks</b></font>", styles['Heading2']))
        document_content.append(Spacer(1, 5))
        for item in risk_insights:
            document_content.append(Paragraph(f"• {item}", styles['Normal']))
