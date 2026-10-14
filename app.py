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

def generate_pdf_report(financials, risks, operations):
    """Generates an enterprise-ready PDF report using ReportLab."""
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
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    story.append(Paragraph("🔷 Limitless Blue | Compliance & Analysis Report", title_style))
    story.append(Paragraph("Generated automatically by the Enterprise Document Intelligence Engine.", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Financial Section
    story.append(Paragraph("1. Financial Parameters & Metrics", section_style))
    if financials:
        data = [["Source File", "Extracted Insight Statement"]]
        for src, text in financials:
            data.append([src, Paragraph(text, body_style)])
        t = Table(data, colWidths=[120, 440])
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
        story.append(Paragraph("No tracked financial data identifiers found.", styles['Italic']))
        
    story.append(Spacer(1, 15))
    
    # Risks Section
    story.append(Paragraph("2. Regulatory & Legal Risk Profile", section_style))
    if risks:
        data = [["Source File", "Extracted Risk Warning"]]
        for src, text in risks:
            data.append([src, Paragraph(text, body_style)])
        t = Table(data, colWidths=[120, 440])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#991b1b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fef2f2')])
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No critical regulatory risks triggered.", styles['Italic']))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

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

        fin_pattern = re.compile(r'\b(revenue|profit|loss|quarterly|fiscal year|ebitda|capEx|operating cost|annual budget|cash flow|usd|eur|expenses)\b', re.IGNORECASE)
        risk_pattern = re.compile(r'\b(non-compliance|regulatory breach|class action|lawsuit|indemnification|liability|intellectual property infringement|termination clause|material adverse effect|dispute resolution)\b', re.IGNORECASE)
        op_pattern = re.compile(r'\b(protocol|tenet|must|extract|auth|step|schedul|scrub)\b', re.IGNORECASE)

        for name, text_content in all_files_data.items():
            sentences = re.split(r'(?<!\b(?:Corp|Inc|Ltd|vs))\.(?=\s|[A-Z])', text_content)
            for sentence in sentences:
                clean_sentence = sentence.strip().replace('\n', ' ')
                if len(clean_sentence) < 15:
                    continue
                if fin_pattern.search(clean_sentence):
                    combined_financials.append((name, clean_sentence))
                if risk_pattern.search(clean_sentence):
                    combined_risks.append((name, clean_sentence))
                if op_pattern.search(clean_sentence):
                    combined_operations.append((name, clean_sentence))

        financial_insights = list(set(combined_financials))[:6]
        risk_insights = list(set(combined_risks))[:6]
        operational_insights = list(set(combined_operations))[:6]

    except Exception as e:
        st.error(f"An unexpected data layout extraction fault occurred: {str(e)}")
        financial_insights, risk_insights, operational_insights = [], [], []

    # 4. Display Extracted Insights UI Elements
    st.subheader("📋 Executive Intelligence Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💵 Financial Metrics & Performance")
        if financial_insights:
            for origin, item in financial_insights:
                st.markdown(f"<div class='metric-box'><b>[FINANCIAL - {origin}]</b> {item}</div>", unsafe_allow_html=True)
        else:
