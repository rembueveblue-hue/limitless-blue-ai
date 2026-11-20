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

STOPWORDS = {"the", "and", "for", "that", "this", "with", "from", "are", "was", "were", "been", "have", "has", "had", "not", "but", "what", "all", "when", "can", "will", "would", "could", "should", "may", "might", "into", "such", "their", "there", "these", "those", "which", "where", "who", "than", "then", "also", "any", "each", "other", "some", "more", "most", "only", "very"}

def clean_text(raw):
    t = unicodedata.normalize("NFKC", raw)
    t = re.sub(r'-\s*\n\s*', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def valid_sent(s):
    low = s.lower()
    if len(s) < 30 or len(s) > 450:
        return False
    if any(n in low for n in ["http://", "https://", "www.", "author help", "submitted online", "copyright ©", "all rights reserved"]):
        return False
    return len(re.findall(r'[a-zA-Z]{2,}', s)) >= 5

def extract_stream(f_obj, ext):
    if ext == "pdf":
        return " ".join(p.extract_text() or "" for p in PdfReader(f_obj).pages)
    if ext == "docx":
        return docx2txt.process(f_obj) or ""
    if ext == "txt":
        raw = f_obj.read()
        return raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw
    return ""

def analyze_docs(doc_map):
    words = Counter()
    doc_sents = {}
    for fname, raw in doc_map.items():
        cleaned = clean_text(raw)
        if cleaned:
            sents = [s.strip() for s in re.split(r'(?<=[\.!?])\s+', cleaned) if valid_sent(s.strip())]
            doc_sents[fname] = sents
            for s in sents:
                words.update(w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', s) if w.lower() not in STOPWORDS)

    themes = {w for w, _ in words.most_common(25)}
    m_pat = re.compile(r'(\$|€|£|¥|zar|usd|eur|gbp|\b\d+(?:\.\d+)?%|\b\d+\s*(?:hours?|days?|weeks?|months?|years?|tons?|units?|mw|kw|gb|tb|mb)\b|\b(?:cost|fee|budget|revenue|margin|invoice|quota|limit|threshold|rate|price|amount)\b)', re.I)
    r_pat = re.compile(r'\b(liabilit\w*|breach\w*|damages|nda|nondisclosure|penalt\w*|guilty|negligen\w*|deficien\w*|risk\w*|exposure|violat\w*|terminat\w*|indemnif\w*|forfeit\w*|allegation\w*|hazard\w*|discrepanc\w*|non-?compliance|default\w*|audit\w*)\b', re.I)
    o_pat = re.compile(r'\b(must|shall|required|mandat\w*|protocol\w*|compl\w*|procedure\w*|maintain\w*|verif\w*|authoriz\w*|enforc\w*|deliver\w*|approv\w*|ensur\w*|govern\w*|standard\w*)\b', re.I)

    fin, ops, rsk, seen = [], [], [], set()
    multi = len(doc_sents) > 1

    for fname, sents in doc_sents.items():
        tag = fname.split("/")[-1]
        for s in sents:
            key = s.lower()
            if key in seen:
                continue
            score = len(set(re.findall(r'\b[a-zA-Z]{4,}\b', key)).intersection(themes))
            rh, mh, oh = len(r_pat.findall(s)), len(m_pat.findall(s)), len(o_pat.findall(s))
            label = f"[{tag}] {s}" if multi else s
            if rh > 0 and rh >= mh and rh >= oh:
                rsk.append((rh * 3 + score, label))
                seen.add(key)
            elif mh > 0 and mh >= oh:
                fin.append((mh * 3 + score, label))
                seen.add(key)
            elif oh > 0:
                ops.append((oh * 3 + score, label))
                seen.add(key)

    cap = min(15, max(6, len(doc_sents) * 2)) if multi else 6
    fin.sort(reverse=True)
    ops.sort(reverse=True)
    rsk.sort(reverse=True)
    return [x[1] for x in fin[:cap]], [x[1] for x in ops[:cap]], [x[1] for x in rsk[:cap]], len(doc_sents)

def build_report(fmt, name, metrics, operational, risk, count):
    sections = [
        ("Key Figures, Metrics & Deadlines", "#1e3a8a", metrics),
        ("Core Mandates & Operational Rules", "#1e3a8a", operational),
        ("Critical Risks & Exposure", "#7f1d1d", risk)
    ]
    sub = f"Source: {name} ({count} document{'s' if count != 1 else ''} processed in-memory)"
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE EXECUTIVE REPORT\n{sub}\n" + "="*55 + "\n\n"
        for title, _, data in sections:
            if data:
                rep += f"[{title.upper()}]\n" + "\n".join(f"- {i}" for i in data) + "\n\n"
        return rep.encode("utf-8")
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        doc.add_paragraph(sub)
        for title, _, data in sections:
            if data:
                doc.add_heading(title, level=1)
                for i in data:
                    doc.add_paragraph(i, style="List Bullet")
        out = io.BytesIO()
        doc.save(out)
        return out.getvalue()
    else:
        out = io.BytesIO()
        p_doc = SimpleDocTemplate(out, pagesize=letter, title="Limitless Blue Executive Report")
        stls = getSampleStyleSheet()
        ctx = [
            Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls["Title"]),
            Paragraph(f"<font size=10 color='#475569'>{html.escape(sub)}</font>", stls["Normal"]),
            Spacer(1, 15)
        ]
        for title, color, data in sections:
            if data:
                ctx.append(Paragraph(f"<font size=14 color='{color}'><b>{title}</b></font>", stls["Heading2"]))
                for i in data:
                    ctx.append(Paragraph(f"• {html.escape(i)}", stls["Normal"]))
                ctx.append(Spacer(1, 10))
        p_doc.build(ctx)
        return out.getvalue()

st.markdown("# 💎 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP)", type=["pdf", "docx", "txt", "zip"])

if "fin" not in st.session_state:
    st.session_state.fin, st.session_state.ops, st.session_state.rsk, st.session_state.cnt, st.session_state.active_fn = [], [], [], 0, None

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        ext = uploaded_file.name.split(".")[-1].lower()
        doc_map = {}
        try:
            if ext == "zip":
                with zipfile.ZipFile(uploaded_file) as z:
                    entries = [i for i in z.infolist() if not i.filename.startswith("__MACOSX/") and not i.is_dir() and i.filename.split(".")[-1].lower() in {"pdf", "docx", "txt"}][:100]
                    for info in entries:
                        inner_ext = info.filename.split(".")[-1].lower()
                        with z.open(info) as f:
                            doc_map[info.filename] = extract_stream(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext)
            else:
                doc_map[uploaded_file.name] = extract_stream(uploaded_file, ext)

            fin_l, ops_l, rsk_l, cnt = analyze_docs(doc_map)
            if cnt > 0:
                st.session_state.fin, st.session_state.ops, st.session_state.rsk, st.session_state.cnt, st.session_state.active_fn = fin_l, ops_l, rsk_l, cnt, uploaded_file.name
                st.success(f"Successfully analyzed: {uploaded_file.name} ({cnt} document{'s' if cnt != 1 else ''} processed in-memory)")
            else:
                st.warning("No readable text discovered in file contents.")
                st.session_state.active_fn = None
        except Exception as e:
            st.error(f"Parsing Error: {e}")
            st.session_state.active_fn = None

    if st.session_state.active_fn:
        st.subheader("📊 Executive Intelligence Summary")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Key Figures, Metrics & Deadlines")
            if st.session_state.fin:
                for i in st.session_state.fin:
                    st.markdown(f"<div class='metric-box'><b>[METRICS & TIMELINES]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No explicit metrics or strict deadlines detected.")
            st.markdown("#### Core Mandates & Operational Rules")
            if st.session_state.ops:
                for i in st.session_state.ops:
                    st.markdown(f"<div class='metric-box'><b>[MANDATES]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No explicit operational mandates detected.")
        with c2:
            st.markdown("#### Critical Risks & Exposure")
            if st.session_state.rsk:
                for i in st.session_state.rsk:
                    st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No high-severity risk triggers detected.")

