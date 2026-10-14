import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import zipfile
import io
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration & Advanced Responsive Canvas Tuning
st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

# Advanced Responsive Media Queries and Carbon Geometric Tech Background Inject
st.markdown("""
    <style>
    /* Premium Carbon & Deep Blue Abstract Mesh Grid Background Matrix */
    .stApp {
        background-color: #060b13;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 64, 175, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(29, 78, 216, 0.1) 0px, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 24px 24px, 24px 24px;
        color: #ffffff;
    }
    
    /* Smart Fluid Header Rules for Multifunctional Mobile vs Laptop Scaling */
    .responsive-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #4e8cff;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .responsive-sub {
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 20px;
    }
    
    @media (max-width: 768px) {
        .responsive-header { font-size: 22px !important; }
        .responsive-sub { font-size: 13px !important; }
        h4 { font-size: 15px !important; }
    }
    @media (min-width: 769px) {
        .responsive-header { font-size: 34px !important; }
        .responsive-sub { font-size: 17px !important; }
    }

    h4 { color: #f8fafc; border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    .metric-box { padding: 14px; background-color: rgba(22, 34, 56, 0.7); border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; backdrop-filter: blur(4px); }
    .risk-box { padding: 14px; background-color: rgba(43, 22, 29, 0.7); border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; backdrop-filter: blur(4px); }
    </style>
    """, unsafe_allow_html=True)

# 2. Fluid Executive Header Injection
st.markdown("<div class='responsive-header'>🔷 Limitless Blue | Enterprise Document Intelligence Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='responsive-sub'>Secure, localized data extraction for corporate and legal compliance evaluation.</div>", unsafe_allow_html=True)
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

def generate_pdf_report(report_data):
    """Generates a clean PDF document using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1d4ed8'),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    story.append(Paragraph("🔷 Limitless Blue | Analysis Report", title_style))
    story.append(Paragraph("Generated automatically by the Enterprise Document Intelligence Engine.", styles['Normal']))
    story.append(Spacer(1, 15))
    
    if report_data:
        data = [["Source File", "Extracted Content Statement"]]
        for src, text in report_data.items():
            # Truncate large texts safely for the PDF preview limit
            preview_text = text[:600] + "..." if len(text) > 600 else text
            data.append([src, Paragraph(preview_text, body_style)])
        
        # Fixed explicit column dimensions prevents engine text wrapping failures
        t = Table(data, colWidths=[130, 400])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No processed data statements found to extract.", styles['Italic']))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# Setup variables globally so they are always ready
all_files_data = {}

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_bytes = uploaded_file.read()
    
    if file_name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            for z_info in z.infolist():
                if not z_info.is_dir() and z_info.filename.split(".")[-1].lower() in ["pdf", "docx", "txt"]:
                    name = z_info.filename.split("/")[-1]
                    content = process_single_file(name, z.read(z_info.filename))
                    if content.strip():
                        all_files_data[name] = content
        st.success(f"Successfully processed ZIP archive: {len(all_files_data)} target documents.")
    else:
        content = process_single_file(file_name, file_bytes)
        if content.strip():
            all_files_data[file_name] = content
        st.success(f"Successfully analyzed: {file_name}")

# 4. Display Extracted Insights UI Elements
st.subheader("📋 Executive Intelligence Summary")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📄 Document Extractions Summary")
    if all_files_data:
        for origin, item in all_files_data.items():
            st.markdown(f"<div class='metric-box'><b>[SOURCE - {origin}]</b> {item[:300]}...</div>", unsafe_allow_html=True)
    else:
        st.info("Awaiting document upload inputs.")
        
with col2:
    st.markdown("#### ⚙️ Engine Directives Status")
    if all_files_data:
        st.info("System successfully mapped layout constraints. PDF compilation asset targets ready.")
    else:
        st.info("No logs present.")

# 5. Export Reporting Block (Completely flat layout, no indentation risk)
st.markdown("---")
st.subheader("💾 Export Findings")

if all_files_data:
    pdf_data = generate_pdf_report(all_files_data)
    st.download_button(
        label="📥 Download Executive Summary PDF Report",
        data=pdf_data,
        file_name="Limitless_Blue_Executive_Report.pdf",
        mime="application/pdf"
    )
else:
    st.warning("Upload files containing valid analytical contexts to enable compilation functions.")
