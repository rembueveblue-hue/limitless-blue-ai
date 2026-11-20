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
from reportlab.lib.styles import getSampleStyleSheet
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
    "the", "and", "for", "that", "this", "with", "from", "are", "was", "were",
    "been", "have", "has", "had", "not", "but", "what", "all", "when", "can",
    "will", "would", "could", "should", "may", "might", "into", "such", "their",
    "there", "these", "those", "which", "where", "who", "whom", "whose", "than",
    "then", "also", "any", "each", "other", "some", "more", "most", "only", "very"
}

def clean_extracted_text(raw_text):
    text = unicodedata.normalize("NFKC", raw_text)
    text = re.sub(r'-\s*\n\s*', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_valid_sentence(s):
    s_low = s.lower()
    if len(s) < 30 or len(s) > 450:
        return False
    noise_markers = [
        "http://", "https://", "www.", "author help", "submitted online",
        "copyright ©", "all rights reserved", "page ", "table of contents"
    ]
    if any(n in s_low for n in noise_markers):
        return False
    # Reject sentences that are mostly numbers/symbols with too few real words
    words = re.findall(r'[a-zA-Z]{2,}', s)
    return len(words) >= 5

def extract_single_stream(f_obj, ext):
    if ext == "pdf":
        reader = PdfReader(f_obj)
        return " ".join(p.extract_text() or "" for p in reader.pages)
    elif ext == "docx":
        return docx2txt.process(f_obj) or ""
    elif ext == "txt":
        raw = f_obj.read()
        return raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw
    return ""

def analyze_documents(doc_map):
    """
    Universal B2B Intelligence Scorer:
    Adapts to any sector by scoring structural patterns + corpus term density
    across single files or 100-file ZIP archives.
    """
    all_words = Counter()
    doc_sentences = {}

    for fname, raw_txt in doc_map.items():
        cleaned = clean_extracted_text(raw_txt)
        if not cleaned:
            continue
        sents = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', cleaned) if is_valid_sentence(s.strip())]
        doc_sentences[fname] = sents
        for s in sents:
            tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', s) if w.lower() not in STOPWORDS]
            all_words.update(tokens)

    top_themes = {w for w, _ in all_words.most_common(25)}

    # Universal structural patterns (works across finance, legal, medical, logistics, engineering)
    metric_pattern = re.compile(
        r'(\$|€|£|¥|zar|usd|eur|gbp|\b\d+(?:\.\d+)?%|\b\d+\s*(?:hours?|days?|weeks?|months?|years?|tons?|units?|mw|kw|gb|tb|mb)\b|\b(?:cost|fee|budget|revenue|margin|invoice|quota|limit|threshold|rate|price|amount)\b)',
        re.IGNORECASE
    )
    risk_pattern = re.compile(
        r'\b(liabilit\w*|breach\w*|damages|nda|nondisclosure|penalt\w*|guilty|negligen\w*|deficien\w*|risk\w*|exposure|violat\w*|terminat\w*|indemnif\w*|forfeit\w*|allegation\w*|hazard\w*|discrepanc\w*|non-?compliance|default\w*|audit\w*)\b',
        re.IGNORECASE
    )
    mandate_pattern = re.compile(
        r'\b(must|shall|required|mandat\w*|protocol\w*|compl\w*|procedure\w*|maintain\w*|verif\w*|authoriz\w*|enforc\w*|deliver\w*|approv\w*|ensur\w*|govern\w*|standard\w*)\b',
        re.IGNORECASE
    )

    scored_metrics, scored_mandates, scored_risks = [], [], []
    seen = set()
    multi_file = len(doc_sentences) > 1

    for fname, sents in doc_sentences.items():
        short_name = fname.split("/")[-1]
        for s in sents:
            norm_key = s.lower()
            if norm_key in seen:
                continue

            tokens = set(re.findall(r'\b[a-zA-Z]{4,}\b', norm_key))
            theme_score = len(tokens.intersection(top_themes))

            r_hits = len(risk_pattern.findall(s))
            m_hits = len(metric_pattern.findall(s))
            o_hits = len(mandate_pattern.findall(s))

            label = f"[{short_name}] {s}" if multi_file else s

            if r_hits > 0 and r_hits >= m_hits and r_hits >= o_hits:
                scored_risks.append((r_hits * 3 + theme_score, label))
                seen.add(norm_key)
            elif m_hits > 0 and m_hits >= o_hits:
                scored_metrics.append((m_hits * 3 + theme_score, label))
                seen.add(norm_key)
            elif o_hits > 0:
                scored_mandates.append((o_hits * 3 + theme_score, label))
                seen.add(norm_key)

    # Scale summary depth automatically: 6 bullets for single file, up to 15 for multi-file ZIPs
    cap = min(15, max(6, len(doc_sentences) * 2)) if multi_file else 6

    scored_metrics.sort(key=lambda x: x[0], reverse=True)
    scored_mandates.sort(key=lambda x: x[0], reverse=True)
    scored_risks.sort(key=lambda x: x[0], reverse=True)

    return (
        [item for _, item in scored_metrics[:cap]],
        [item for _, item in scored_mandates[:cap]],
        [item for _, item in scored_risks[:cap]],
        len(doc_sentences)
    )

def build_report(fmt, name, metrics, operational, risk, file_count):
    sections = [
        ("Key Figures, Metrics & Deadlines", "#1e3a8a", metrics),
        ("Core Mandates & Operational Rules", "#1e3a8a", operational),
        ("Critical Risks & Exposure", "#7f1d1d", risk)
    ]
    subtitle = f"Source: {name} ({file_count} document{'s' if file_count != 1 else ''} processed in-memory)"

    if "txt" in fmt:
        rep = f"LIMITLESS BLUE EXECUTIVE REPORT\n{subtitle}\n" + "="*55 + "\n\n"
        for title, _, dataset in sections:
            if dataset:
                rep += f"[{title.upper()}]\n" + "\n".join([f"- {item}" for item in dataset]) + "\n\n"
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        doc.add_paragraph(subtitle)
        for title, _, dataset in sections:
            if dataset:
                doc.add_heading(title, level=1)
                for item in dataset:
                    doc.add_paragraph(item, style='List Bullet')
        out = io.BytesIO()
        doc.save(out)
        return out.getvalue()
    else:
        out = io.BytesIO()
        p_doc = SimpleDocTemplate(out, pagesize=letter, title="Limitless Blue Executive Report")
        stls = getSampleStyleSheet()
        ctx = [
            Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']),
            Paragraph(f"<font size=10 color='#475569'>{html.escape(subtitle)}</font>", stls['Normal']),
            Spacer(1, 15)
        ]
        for title, color, dataset in sections:
            if dataset:
                ctx.append(Paragraph(f"<font size=14 color='{color}'><b>{title}</b></font>", stls['Heading2']))
                for item in dataset:
                    ctx.append(Paragraph(f"• {html.escape(item)}", stls['Normal']))
                ctx.append(Spacer(1, 10))
        p_doc.build(ctx)
        return out.getvalue()

st.markdown("# 💎 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP)", type=["pdf", "docx", "txt", "zip"])

if "fin" not in st.session_state:
    st.session_state.fin = []
    st.session_state.ops = []
    st.session_state.rsk = []
    st.session_state.file_count = 0
    st.session_state.active_fn = None

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        ext = uploaded_file.name.split(".")[-1].lower()
        doc_map = {}
        try:
            if ext == "zip":
                with zipfile.ZipFile(uploaded_file) as z:
                    valid_entries = [
                        info for info in z.infolist()
                        if not info.filename.startswith('__MACOSX/') and not info.is_dir()
                        and info.filename.split(".")[-1].lower() in {"pdf", "docx", "txt"}
                    ][:100]  # Hard cap at 100 files per enterprise archive

                    for info in valid_entries:
                        inner_ext = info.filename.split(".")[-1].lower()
                        with z.open(info) as f:
                            stream = io.BytesIO(f.read()) if inner_ext != "txt" else f
                            doc_map[info.filename] = extract_single_stream(stream, inner_ext)
            else:
                doc_map[uploaded_file.name] = extract_single_stream(uploaded_file, ext)

            fin_list, ops_list, rsk_list, processed_count = analyze_documents(doc_map)

            if fin_list or ops_list or rsk_list or processed_count > 0:
