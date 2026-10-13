import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import zipfile
import io
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b111e; color: #ffffff; }
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h3 { color: #94a3b8; font-weight: 400; }
    h4 { color: #f8fafc; border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .metric-box { padding: 14px; background-color: #162238; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: #2b161d; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# 2. Executive Header Layout
st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

# 3. File Processing Module Supporting ZIP, PDF, DOCX, and TXT
uploaded_file = st.file_uploader("Upload Corporate Files (PDF, DOCX, TXT, or ZIP Archive)", type=["pdf", "docx", "txt", "zip"])

def process_single_file(file_name, file_bytes):
    text_content = ""
    file_type = file_name.split(".")[-1].lower()
    if file_type == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text_content += page.extract_text() or ""
    elif file_type == "docx":
        text_content = docx2txt.process(io.BytesIO(file_bytes))
    elif file_type == "txt":
        text_content = file_bytes.decode("utf-8", errors="ignore")
    return text_content

if uploaded_file is not None:
    all_files_data = {}
    file_name = uploaded_file.name
    file_bytes = uploaded_file.read()
    
    try:
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                for z_info in z.infolist():
                    if not z_info.is_dir() and z_info.filename.split(".")[-1].lower() in ["pdf", "docx", "txt"]:
                        name = z_info.filename.split("/")[-1]
                        content = process_single_file(name, z.read(z_info.filename))
                        if content.strip():
                            all_files_data[name] = content
            st.success(f"Successfully extracted and unpacked ZIP archive: {len(all_files_data)} target documents processed.")
        else:
            content = process_single_file(file_name, file_bytes)
            if content.strip():
                all_files_data[file_name] = content
            st.success(f"Successfully analyzed: {file_name}")

        combined_financials = []
        combined_risks = []
        combined_operations = []

        for name, text_content in all_files_data.items():
            sentences = re.split(r'(?<=[.!?])\s+', text_content)
            for sentence in sentences:
                s_lower = sentence.lower()
                if any(k in s_lower for k in ["$", "revenue", "profit", "expenditure", "cost", "margin", "penalty"]):
                    if len(sentence.strip()) > 15: combined_financials.append((name, sentence.strip()))
                if any(k in s_lower for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty"]):
                    if len(sentence.strip()) > 15: combined_risks.append((name, sentence.strip()))
                if any(k in s_lower for k in ["protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub"]):
                    if len(sentence.strip()) > 15: combined_operations.append((name, sentence.strip()))

        financial_insights = list(set(combined_financials))[:6]
        risk_insights = list(set(combined_risks))[:6]
        operational_insights = list(set(combined_operations))[:6]

        # --- DYNAMIC DASHBOARD SCREEN OUTPUT ---
        st.subheader("📋 Executive Intelligence Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Financial Metrics & Performance")
            if financial_insights:
                for origin, item in financial_insights:
                    st.markdown(f"<div class='metric-box'><b>[FINANCIAL - {origin}]</b> {item}</div>", unsafe_allow_html=True)
            else:
                st.info("No explicitly isolated financial metrics found.")
                
            st.markdown("#### Strategic & Operational Directives")
            if operational_insights:
                for origin, item in operational_insights:
                    st.markdown(f"<div class='metric-box'><b>[OPERATIONS - {origin}]</b> {item}</div>", unsafe_allow_html=True)
            else:
                st.info("No distinct operational steps detected.")

        with col2:
            st.markdown("#### Legal Liabilities & Risk Assessment")
            if risk_insights:
                for origin, item in risk_insights:
                    st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK - {origin}]</b> {item}</div>", unsafe_allow_html=True)
            else:
                st.info("No critical legal compliance flags detected.")
                
            # Dynamic Density Tracker Graph
            st.markdown("#### Data Extraction Insights Density")
            metric_counts = {
                "Metrics": ["Financial Elements", "Operational Steps", "Risk Factors"],
                "Count": [len(financial_insights), len(operational_insights), len(risk_insights)]
            }
            chart_df = pd.DataFrame(metric_counts)
            st.bar_chart(data=chart_df, x="Metrics", y="Count", use_container_width=True)
        
        st.markdown("---")
        
        # --- MULTI-FORMAT ENTERPRISE EXPORT ENGINE HUB ---
        st.subheader("📥 Export Intelligence Report Hub")
        format_choice = st.selectbox("Select Export Format Preference:", ["Portable Document Format (.pdf)", "Microsoft Word (.docx)", "Plain Text Document (.txt)"])
        
        def build_txt_report():
            report = "LIMITLESS BLUE EXECUTIVE SUMMARY INTEL\n" + "="*50 + "\n\n"
            report += "[FINANCIAL METRICS]\n" + "\n".join([f"• [{origin}] {f}" for origin, f in financial_insights]) + "\n\n"
            report += "[OPERATIONAL DIRECTIVES]\n" + "\n".join([f"• [{origin}] {o}" for origin, o in operational_insights]) + "\n\n"
            report += "[LEGAL RISK ASSESSMENT]\n" + "\n".join([f"• [{origin}] {r}" for origin, r in risk_insights]) + "\n"
            return report.encode('utf-8')

        def build_docx_report():
            doc = Document()
            doc.add_heading("Limitless Blue AI | Executive Report", 0)
            doc.add_heading("Financial Insights", level=1)
            for origin, item in financial_insights: doc.add_paragraph(f"[{origin}] {item}", style='List Bullet')
            doc.add_heading("Operational Directives", level=1)
            for origin, item in operational_insights: doc.add_paragraph(f"[{origin}] {item}", style='List Bullet')
            doc.add_heading("Legal Liabilities & Risks", level=1)
            for origin, item in risk_insights: doc.add_paragraph(f"[{origin}] {item}", style='List Bullet')
            target_stream = io.BytesIO()
            doc.save(target_stream)
            return target_stream.getvalue()

        def build_pdf_report():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, title="Limitless Blue Executive Report")
            styles = getSampleStyleSheet()
            
            body_style = ParagraphStyle('ReportBody', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
            fin_box_style = ParagraphStyle('FinBoxText', parent=body_style, textColor=colors.HexColor('#1e40af'))
            risk_box_style = ParagraphStyle('RiskBoxText', parent=body_style, textColor=colors.HexColor('#991b1b'))
            
            story = [
                Paragraph("<font size=24 color='#1d4ed8'><b>🔷 Limitless Blue Intelligence</b></font>", styles['Title']),
                Paragraph("<b>Executive Data Extraction Analysis Report</b>", styles['Normal']),
                Spacer(1, 15)
            ]
            
            story.append(Paragraph("<font size=14 color='#1e3a8a'><b>💵 Financial & Operational Directives Summary</b></font>", styles['Heading2']))
            story.append(Spacer(1, 5))
            for origin, item in financial_insights + operational_insights:
                p = Paragraph(f"<b>[{origin}]</b> {item}", fin_box_style)
                t = Table([[p]], colWidths=[500])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bfdbfe')),
                    ('PADDING', (0,0), (-1,-1), 10),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
                
            story.append(Spacer(1, 10))
            story.append(Paragraph("<font size=14 color='#7f1d1d'><b>🚨 Legal Liability & Compliance Exposure Risks</b></font>", styles['Heading2']))
            story.append(Spacer(1, 5))
            for origin, item in risk_insights:
                p = Paragraph(f"<b>[{origin}]</b> {item}", risk_box_style)
                t = Table([[p]], colWidths=[500])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
