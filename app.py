import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import io
import html
import unicodedata
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

def clean_sentence(s):
    s = unicodedata.normalize("NFKC", s)
    # Remove stray box/bullet icons (■, ●, •, etc.)
    s = re.sub(r'[\u25a0-\u25ff\u2022\u2023\u25e6\u2043]\s*', '', s)
    # Remove leading dashes or dangling list numbers
    s = re.sub(r'^[\-\—\–\:\d\.\)\s]+', '', s)
    s = re.sub(r'\s+\d+\.$', '.', s)
    return re.sub(r'\s+', ' ', s).strip()

# Isolated data compilation engine prevents document generation faults on web links
def build_report(fmt, name, financial, operational, risk):
    summary_line = (
        f"Executive Audit of {name}: Identified {len(financial)} key financial metric(s), "
        f"{len(operational)} operational directive(s), and {len(risk)} critical risk factor(s)."
    )
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE EXECUTIVE REPORT:\n{name.upper()}\n" + "="*50 + "\n"
        rep += f"{summary_line}\n\n"
        rep += "[FINANCIAL METRICS]\n" + "\n".join([f"- {f}" for f in financial]) + "\n\n"
        rep += "[OPERATIONAL DIRECTIVES]\n" + "\n".join([f"- {o}" for o in operational]) + "\n\n"
        rep += "[CRITICAL RISKS]\n" + "\n".join([f"- {r}" for r in risk])
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        doc.add_paragraph(summary_line)
        for title, dataset in [("Financial Metrics", financial), ("Operational Directives", operational), ("Critical Risks", risk)]:
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
        bullet_style = ParagraphStyle('BulletItem', parent=stls['Normal'], spaceAfter=6, leftIndent=12, leading=14)
        ctx = [
            Paragraph("<font size=20 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']),
            Paragraph(f"<font size=9 color='#475569'><i>{html.escape(summary_line)}</i></font>", stls['Normal']),
            Spacer(1, 12)
        ]
        for h, c, l in [("Financial Metrics", "#1e3a8a", financial), ("Operational Directives", "#1e3a8a", operational), ("Critical Risks", "#7f1d1d", risk)]:
            ctx.append(Paragraph(f"<font size=13 color='{c}'><b>{h}</b></font>", stls['Heading2']))
            for item in l:
                ctx.append(Paragraph(f"• {html.escape(item)}", bullet_style))
            ctx.append(Spacer(1, 8))
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
    st.session_state.active_fn = None

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        txt, ext = "", uploaded_file.name.split(".")[-1].lower()
        file_count = 1
        try:
            def extract(f_obj, e):
                if e == "pdf": return "\n".join([p.extract_text() or "" for p in PdfReader(f_obj).pages])
                if e == "docx": return docx2txt.process(f_obj)
                if e == "txt": return f_obj.read().decode("utf-8", errors="ignore")
                return ""
            
            if ext == "zip":
                chunks = []
                with zipfile.ZipFile(uploaded_file) as z:
                    entries = [i for i in z.infolist() if not i.filename.startswith('__MACOSX/') and not i.is_dir()][:100]
                    file_count = len(entries)
                    for info in entries:
                        inner_ext = info.filename.split(".")[-1].lower()
                        with z.open(info) as f:
                            chunks.append(extract(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext))
                txt = "\n".join(chunks)
            else:
                txt = extract(uploaded_file, ext)
                
            if txt.strip():
                # Collapse newlines into spaces naturally without breaking sentences
                clean_txt = re.sub(r'\s+', ' ', txt)
                sentences = re.split(r'(?<=[\.!?])\s+', clean_txt)
                
                cap = min(15, max(5, file_count * 2)) if ext == "zip" else 5
                seen = set()
                fin_list, rsk_list, ops_list = [], [], []

                for raw_s in sentences:
                    s = clean_sentence(raw_s)
                    if 15 < len(s) < 420 and s not in seen:
                        s_low = s.lower()
                        # Priority routing prevents the same sentence from duplicating across boxes
                        if any(k in s_low for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "restrict", "penalty", "risk", "exposure"]) and len(rsk_list) < cap:
                            rsk_list.append(s)
                            seen.add(s)
                        elif any(k in s_low for k in ["$", "€", "£", "zar", "revenue", "profit", "expenditure", "cost", "margin", "budget", "%"]) and len(fin_list) < cap:
                            fin_list.append(s)
                            seen.add(s)
                        elif any(k in s_low for k in ["protocol", "tenet", "must", "shall", "required", "extract", "auth", "step", "schedul", "scrub", "comply", "compliance"]) and len(ops_list) < cap:
                            ops_list.append(s)
                            seen.add(s)

                st.session_state.fin = fin_list
                st.session_state.rsk = rsk_list
                st.session_state.ops = ops_list
                st.session_state.active_fn = uploaded_file.name
                st.success(f"Successfully analyzed: {uploaded_file.name}")
            else:
                st.warning("No readable text discovered in file contents.")
                st.session_state.active_fn = None
        except Exception as e:
            st.error(f"Parsing Error: {e}")
            st.session_state.active_fn = None

    # Steady UI layout draws from cached computations without repeating extract sweeps
    if st.session_state.active_fn:
        st.subheader("📊 Executive Intelligence Summary")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Financial Metrics & Performance")
            for i in st.session_state.fin: st.markdown(f"<div class='metric-box'><b>[FINANCIAL]</b> {i}</div>", unsafe_allow_html=True)
            st.markdown("#### Strategic & Operational Directives")
            for i in st.session_state.ops: st.markdown(f"<div class='metric-box'><b>[OPERATIONS]</b> {i}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("#### Legal Liabilities & Risk Assessment")
            for i in st.session_state.rsk: st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {i}</div>", unsafe_allow_html=True)
            
        st.bar_chart(pd.DataFrame({"Metrics": ["Financial", "Operational", "Risk"], "Count": [len(st.session_state.fin), len(st.session_state.ops), len(st.session_state.rsk)]}), x="Metrics", y="Count", use_container_width=True)
        st.markdown("---")
        
        st.subheader("📥 Export Intelligence Report Hub")
        fmt = st.selectbox("Select Export Format Preference:", ["Portable Document Format (.pdf)", "Microsoft Word (.docx)", "Plain Text Document (.txt)"])
        ext_m = "pdf" if "pdf" in fmt else "docx" if "docx" in fmt else "txt"
        
        st.download_button(
            label=f"📥 Download Summary Report (.{ext_m})", 
            data=build_report(ext_m, st.session_state.active_fn, st.session_state.fin, st.session_state.ops, st.session_state.rsk), 
            file_name=f"Intel_Report_{st.session_state.active_fn}.{ext_m}", 
            mime=f"application/{ext_m}" if ext_m != "txt" else "text/plain"
        )
else:
    st.session_state.fin, st.session_state.ops, st.session_state.rsk, st.session_state.active_fn = [], [], [], None
