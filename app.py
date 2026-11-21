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

# Isolated data compilation engine prevents document generation faults on web links
def build_report(fmt, name, metrics, operational, risk):
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE EXECUTIVE RECAP:\n{name.upper()}\n" + "="*50 + "\n\n"
        for title, dataset in [("KEY METRICS & DEADLINES", metrics), ("CORE MANDATES & DIRECTIVES", operational), ("CRITICAL RISKS & EXPOSURE", risk)]:
            rep += f"[{title}]\n" + ("\n".join([f"- {item}" for item in dataset]) if dataset else "None detected.") + "\n\n"
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Limitless Blue Executive Report", 0)
        for title, dataset in [("Key Metrics & Deadlines", metrics), ("Core Mandates & Directives", operational), ("Critical Risks & Exposure", risk)]:
            doc.add_heading(title, level=1)
            for item in (dataset if dataset else ["None detected."]): doc.add_paragraph(item, style='List Bullet')
        out = io.BytesIO(); doc.save(out); return out.getvalue()
    else:
        out = io.BytesIO(); p_doc = SimpleDocTemplate(out, pagesize=letter, title="Limitless Blue Executive Report"); stls = getSampleStyleSheet()
        ctx = [Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']), Spacer(1, 15)]
        for title, color, dataset in [("Key Metrics & Deadlines", "#1e3a8a", metrics), ("Core Mandates & Directives", "#1e3a8a", operational), ("Critical Risks & Exposure", "#7f1d1d", risk)]:
            ctx.append(Paragraph(f"<font size=14 color='{color}'><b>{title}</b></font>", stls['Heading2']))
            for item in (dataset if dataset else ["None detected."]): ctx.append(Paragraph(f"• {html.escape(item)}", stls['Normal']))
            ctx.append(Spacer(1, 10))
        p_doc.build(ctx); return out.getvalue()

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
        try:
            def extract(f_obj, e):
                if e == "pdf": return " ".join([p.extract_text() or "" for p in PdfReader(f_obj).pages])
                if e == "docx": return docx2txt.process(f_obj)
                if e == "txt": return f_obj.read().decode("utf-8", errors="ignore")
                return ""
            
            if ext == "zip":
                with zipfile.ZipFile(uploaded_file) as z:
                    for info in z.infolist():
                        if not info.filename.startswith('__MACOSX/') and not info.is_dir():
                            inner_ext = info.filename.split(".")[-1].lower()
                            with z.open(info) as f: 
                                txt += extract(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext) + " "
            else:
                txt = extract(uploaded_file, ext)
                
            if txt.strip():
                txt = unicodedata.normalize("NFKC", txt)
                sentences = re.split(r'(?<=[\.!?])\s+', re.sub(r'\s+', ' ', txt))
                fin_list, rsk_list, ops_list, seen = [], [], [], set()
                for s in sentences:
                    s = s.strip()
                    if 25 < len(s) < 400 and s not in seen and "http" not in s.lower():
                        s_low = s.lower()
                        if any(k in s_low for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "restrict", "penalty", "penalties", "guilty", "negligen", "deficien", "risk", "exposure", "violat"]) and len(rsk_list) < 8:
                            rsk_list.append(s); seen.add(s)
                        elif any(k in s_low for k in ["$", "€", "£", "zar", "revenue", "profit", "expenditure", "cost", "margin", "budget", "fee", "amount", "hours", "days", "years", "deadline", "%"]) and len(fin_list) < 8:
                            fin_list.append(s); seen.add(s)
                        elif any(k in s_low for k in ["protocol", "tenet", "must", "shall", "required", "extract", "auth", "step", "schedul", "scrub", "comply", "compliance", "procedure", "maintain", "issued", "acknowledge", "fulfill"]) and len(ops_list) < 8:
                            ops_list.append(s); seen.add(s)
                
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
            st.markdown("#### Key Metrics & Deadlines")
            if st.session_state.fin:
                for i in st.session_state.fin: st.markdown(f"<div class='metric-box'><b>[METRICS]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No explicit metrics or deadlines detected.")
            st.markdown("#### Core Mandates & Directives")
            if st.session_state.ops:
                for i in st.session_state.ops: st.markdown(f"<div class='metric-box'><b>[MANDATES]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No explicit operational mandates detected.")
        with c2:
            st.markdown("#### Critical Risks & Exposure")
            if st.session_state.rsk:
                for i in st.session_state.rsk: st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {i}</div>", unsafe_allow_html=True)
            else:
                st.info("No high-severity risk triggers detected.")
            
        st.bar_chart(pd.DataFrame({"Category": ["Metrics & Deadlines", "Mandates", "Critical Risks"], "Count": [len(st.session_state.fin), len(st.session_state.ops), len(st.session_state.rsk)]}), x="Category", y="Count", use_container_width=True)
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
