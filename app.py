import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import io
import html
import unicodedata
from collections import Counter
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import zipfile

st.set_page_config(page_title="Limitless Blue AI", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h3 { color: var(--text-color); font-weight: 400; opacity: 0.85; }
    h4 { color: var(--text-color); border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    .exec-brief { padding: 15px 18px; background-color: rgba(29, 78, 216, 0.14); color: var(--text-color); border-radius: 8px; margin: 10px 0 18px 0; border-left: 5px solid #1d4ed8; font-size: 14.5px; line-height: 1.6; }
    .metric-box { padding: 14px; background-color: rgba(78, 140, 255, 0.12); color: var(--text-color); border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: rgba(239, 68, 68, 0.12); color: var(--text-color); border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "are", "was", "were", "will", "shall",
    "must", "have", "has", "had", "not", "but", "all", "any", "can", "may", "such", "into",
    "other", "than", "then", "its", "their", "there", "these", "those", "which", "who", "whom",
    "whose", "where", "when", "why", "how", "each", "both", "few", "more", "most", "some", "only",
    "own", "same", "too", "very", "also", "been", "being", "does", "did", "doing", "would", "could",
    "should", "might", "about", "above", "after", "again", "against", "before", "below", "between",
    "during", "further", "here", "once", "over", "under", "until", "while", "within", "without",
    "section", "document", "report", "page", "date", "file", "information", "based", "including"
}

def repair_text(raw_text):
    txt = unicodedata.normalize("NFKC", raw_text)
    txt = re.sub(r'([a-zA-Z])-\s*\n\s*([a-zA-Z])', r'\1\2', txt)
    txt = re.sub(r'\s+', ' ', txt)
    txt = re.sub(r'\b(f[il])\s+([a-z])', r'\1\2', txt)
    txt = re.sub(r'([a-z])\s+(f[il])\s+([a-z])', r'\1\2\3', txt)
    txt = re.sub(r'[\u25a0-\u25ff\u2022\u2023\u25e6\u2043]\s*', '', txt)
    return txt

def clean_sentence(s):
    s = re.sub(r'^[\-\—\–\:\d\.\)\s]+', '', s)
    s = re.sub(r'\s+\d+\.$', '.', s)
    s = re.sub(r'([:,;])\.', r'\1', s)
    s = re.sub(r'\.{2,}', '.', s)
    return s.strip()

def get_output_standard(text):
    """Adapts the executive output terminology to match the uploaded business domain."""
    low = text.lower()
    words = re.findall(r'\b[a-zA-Z]{4,}\b', low)
    top_terms = [w.capitalize() for w, _ in Counter([w for w in words if w not in STOPWORDS]).most_common(4)]
    subject_focus = ", ".join(top_terms) if top_terms else "Enterprise Governance & Operations"

    if sum(low.count(k) for k in ["patient", "clinical", "diagnosis", "medication", "hospital", "medical", "treatment", "doctor"]) >= 2:
        return {
            "standard": "Clinical & Healthcare Governance",
            "focus": subject_focus,
            "s1_title": "Clinical Parameters, Metrics & Timelines",
            "s1_tag": "CLINICAL",
            "s2_title": "Care Protocols & Medical Record Directives",
            "s2_tag": "PROTOCOL",
            "s3_title": "Clinical Liabilities & Confidentiality Risks",
            "s3_tag": "CRITICAL RISK"
        }
    if sum(low.count(k) for k in ["nondisclosure", "nda", "indemnif", "jurisdiction", "arbitration", "clause", "liquidated damages", "governing law", "covenant"]) >= 2:
        return {
            "standard": "Legal Due Diligence & Contractual Risk",
            "focus": subject_focus,
            "s1_title": "Contractual Thresholds, Consideration & Deadlines",
            "s1_tag": "CONTRACT TERMS",
            "s2_title": "Binding Covenants & Compliance Mandates",
            "s2_tag": "MANDATE",
            "s3_title": "Material Breaches, Indemnities & Legal Exposures",
            "s3_tag": "LEGAL RISK"
        }
    if sum(low.count(k) for k in ["revenue", "profit", "margin", "expenditure", "benchmark", "ledger", "quarter", "fiscal", "ebitda", "budget", "audit"]) >= 2:
        return {
            "standard": "Financial Performance & Corporate Audit",
            "focus": subject_focus,
            "s1_title": "Financial Metrics & Performance Benchmarks",
            "s1_tag": "FINANCIAL",
            "s2_title": "Strategic & Operational Directives",
            "s2_tag": "OPERATIONS",
            "s3_title": "Legal Liabilities & Critical Risk Assessment",
            "s3_tag": "CRITICAL RISK"
        }

    lead = top_terms[0] if top_terms else "Enterprise"
    return {
        "standard": f"{lead} & Commercial Operations",
        "focus": subject_focus,
        "s1_title": "Key Quantitative Metrics, Figures & Deadlines",
        "s1_tag": "KEY METRICS",
        "s2_title": "Strategic & Operational Directives",
        "s2_tag": "DIRECTIVE",
        "s3_title": "Critical Risks, Liabilities & Exposures",
        "s3_tag": "CRITICAL RISK"
    }

# Isolated data compilation engine upgraded for boardroom-ready multi-page output
def build_report(fmt, name, file_count, out_std, financial, operational, risk):
    total = len(financial) + len(operational) + len(risk)
    exec_summary = (
        f"Executive Synthesis of {name} ({file_count} file(s)) | Standard: {out_std['standard']} | "
        f"Core Focus: {out_std['focus']} | Extracted {total} unique intelligence findings "
        f"({len(financial)} quantitative metrics, {len(operational)} operational directives, {len(risk)} critical risk factors)."
    )

    if "txt" in fmt:
        rep = f"LIMITLESS BLUE EXECUTIVE REPORT:\n{name.upper()}\n" + "="*60 + "\n"
        rep += f"{exec_summary}\n\n"
        rep += f"[{out_std['s1_title'].upper()}]\n" + "\n".join([f"- {f}" for f in financial]) + "\n\n"
        rep += f"[{out_std['s2_title'].upper()}]\n" + "\n".join([f"- {o}" for o in operational]) + "\n\n"
        rep += f"[{out_std['s3_title'].upper()}]\n" + "\n".join([f"- {r}" for r in risk])
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        doc.add_paragraph(exec_summary)
        for title, dataset in [(out_std['s1_title'], financial), (out_std['s2_title'], operational), (out_std['s3_title'], risk)]:
            if dataset:
                doc.add_heading(title, level=1)
                for item in dataset:
                    doc.add_paragraph(item, style='List Bullet')
        out = io.BytesIO()
        doc.save(out)
        return out.getvalue()
    else:
        out = io.BytesIO()
        p_doc = SimpleDocTemplate(out, pagesize=letter, topMargin=36, bottomMargin=36, title="Limitless Blue Executive Report")
        stls = getSampleStyleSheet()
        bullet_style = ParagraphStyle('BulletItem', parent=stls['Normal'], spaceAfter=4, leftIndent=12, leading=13.5, fontSize=9.5)
        ctx = [
            Paragraph("<font size=18 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']),
            Paragraph(f"<font size=8.5 color='#475569'><i>{html.escape(exec_summary)}</i></font>", stls['Normal']),
            Spacer(1, 8)
        ]

        tbl = Table([
            [out_std['s1_tag'], out_std['s2_tag'], out_std['s3_tag'], "TOTAL INSIGHTS"],
            [str(len(financial)), str(len(operational)), str(len(risk)), str(total)]
        ], colWidths=[130, 130, 130, 130])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, 1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        ctx.extend([tbl, Spacer(1, 10), HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1")), Spacer(1, 6)])

        for h, c, l in [(out_std['s1_title'], "#1e3a8a", financial), (out_std['s2_title'], "#1e3a8a", operational), (out_std['s3_title'], "#7f1d1d", risk)]:
            if l:
                sec_head = ParagraphStyle('SecHead', parent=stls['Heading2'], fontSize=11.5, textColor=colors.HexColor(c), spaceBefore=6, spaceAfter=4, keepWithNext=True)
                ctx.append(Paragraph(f"<b>{html.escape(h)}</b>", sec_head))
                for item in l:
                    ctx.append(Paragraph(f"• {html.escape(item)}", bullet_style))
                ctx.append(Spacer(1, 6))
        p_doc.build(ctx)
        return out.getvalue()

st.markdown("# 💎 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP)", type=["pdf", "docx", "txt", "zip"])

# Persistent state initialization ensures steady execution loops across user selections
if "fin" not in st.session_state:
