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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import zipfile

st.set_page_config(page_title="Limitless Blue AI", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h3 { color: var(--text-color); font-weight: 400; opacity: 0.8; }
    h4 { color: var(--text-color); border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
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

def detect_output_labels(text):
    low = text.lower()
    words = re.findall(r'\b[a-zA-Z]{4,}\b', low)
    top_terms = [w.capitalize() for w, _ in Counter([w for w in words if w not in STOPWORDS]).most_common(3)]
    focus = ", ".join(top_terms) if top_terms else "Enterprise Operations"

    if sum(low.count(k) for k in ["patient", "clinical", "diagnosis", "medication", "hospital", "medical", "treatment", "doctor"]) >= 2:
        return ("Clinical & Healthcare Standard", focus, "Clinical Parameters & Metrics", "CLINICAL", "Care Protocols & Record Directives", "PROTOCOL", "Clinical Liabilities & Confidentiality Risks", "CRITICAL RISK")
    if sum(low.count(k) for k in ["nondisclosure", "nda", "indemnif", "jurisdiction", "arbitration", "clause", "liquidated damages", "governing law", "covenant"]) >= 2:
        return ("Legal & Regulatory Standard", focus, "Contractual Terms & Thresholds", "LEGAL TERMS", "Binding Covenants & Compliance Mandates", "MANDATE", "Legal Liabilities & Breach Exposures", "LEGAL RISK")
    if sum(low.count(k) for k in ["revenue", "profit", "margin", "expenditure", "benchmark", "ledger", "quarter", "fiscal", "ebitda", "budget", "audit"]) >= 2:
        return ("Financial & Corporate Standard", focus, "Financial Metrics & Performance", "FINANCIAL", "Strategic & Operational Directives", "OPERATIONS", "Legal Liabilities & Critical Compliance Risks", "CRITICAL RISK")

    lead = top_terms[0] if top_terms else "Enterprise"
    return (f"{lead} Industry Standard", focus, f"{lead} Metrics, Figures & Deadlines", "KEY METRICS", "Strategic & Operational Directives", "OPERATIONS", "Critical Risks & Liabilities", "CRITICAL RISK")

# Isolated data compilation engine prevents document generation faults on web links
def build_report(fmt, name, labels, financial, operational, risk):
    std_name, focus, h1, _, h2, _, h3, _ = labels
    summary_line = f"Extracted Executive Summary: {name} | Standard: {std_name} | Key Focus: {focus} ({len(financial) + len(operational) + len(risk)} findings)"

    if "txt" in fmt:
        rep = f"LIMITLESS BLUE RECAP:\n{name.upper()}\n" + "=" * 50 + "\n"
        rep += f"{summary_line}\n\n"
        rep += f"[{h1.upper()}]\n" + "\n".join([f"- {f}" for f in financial]) + "\n\n"
        rep += f"[{h2.upper()}]\n" + "\n".join([f"- {o}" for o in operational]) + "\n\n"
        rep += f"[{h3.upper()}]\n" + "\n".join([f"- {r}" for r in risk])
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        doc.add_paragraph(summary_line)
        for title, dataset in [(h1, financial), (h2, operational), (h3, risk)]:
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
            Paragraph("<font size=20 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']),
            Paragraph(f"<font size=9 color='#475569'><b>{html.escape(summary_line)}</b></font>", stls['Normal']),
            Spacer(1, 10)
        ]
        for h, c, l in [(h1, "#1e3a8a", financial), (h2, "#1e3a8a", operational), (h3, "#7f1d1d", risk)]:
            if l:
                sec_style = ParagraphStyle('SecH', parent=stls['Heading2'], textColor=colors.HexColor(c), fontSize=12, keepWithNext=True)
                ctx.append(Paragraph(f"<b>{html.escape(h)}</b>", sec_style))
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
    st.session_state.fin = []
    st.session_state.ops = []
    st.session_state.rsk = []
    st.session_state.labels = ("Financial & Corporate Standard", "Enterprise", "Financial Metrics & Performance", "FINANCIAL", "Strategic & Operational Directives", "OPERATIONS", "Legal Liabilities & Critical Compliance Risks", "CRITICAL RISK")
    st.session_state.active_fn = None

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        txt, ext = "", uploaded_file.name.split(".")[-1].lower()
        try:
            def extract(f_obj, e):
                if e == "pdf":
                    return "\n".join([p.extract_text() or "" for p in PdfReader(f_obj).pages])
                if e == "docx":
                    return docx2txt.process(f_obj)
                if e == "txt":
                    return f_obj.read().decode("utf-8", errors="ignore")
                return ""

            if ext == "zip":
                chunks = []
                with zipfile.ZipFile(uploaded_file) as z:
                    for info in z.infolist():
                        if not info.filename.startswith('__MACOSX/') and not info.is_dir():
                            inner_ext = info.filename.split(".")[-1].lower()
                            with z.open(info) as f:
                                chunks.append(extract(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext))
                txt = "\n".join(chunks)
            else:
                txt = extract(uploaded_file, ext)

            if txt.strip():
                repaired = repair_text(txt)
                labels = detect_output_labels(repaired)
                sentences = re.split(r'(?<=[\.!?])\s+', repaired)

                seen = set()
                fin_list, rsk_list, ops_list = [], [], []

                risk_kw = ["liabilit", "breach", "damages", "nondisclosure", "nda", "restrict", "penalty", "guilty", "negligen", "deficien", "risk", "exposure", "violat", "hazard", "unsafe", "defect", "delay", "default", "dispute", "confidential", "unauthorized", "misuse", "complication", "discrepanc", "halt", "terminat", "trouble"]
                fin_kw = ["$", "€", "£", "zar", "revenue", "profit", "expenditure", "margin", "fee", "budget", "amount", "hours", "days", "months", "years", "deadline", "%", "benchmark", "rate", "ratio", "total", "average", "threshold", "capacity", "volume", "quota", "patient", "diagnosis", "treatment", "proforma", "sqm", "lease", "rent"]
