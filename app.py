import streamlit as st
from pypdf import PdfReader
import docx2txt
import re
import io
import pandas as pd
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import zipfile

st.set_page_config(page_title="Limitless Blue AI", page_icon="🔷", layout="wide")

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
def build_report(fmt, name, financial, operational, risk):
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE RECAP:\n{name.upper()}\n" + "="*50 + "\n\n"
        rep += "[FINANCIAL]\n" + "\n".join([f"- {f}" for f in financial]) + "\n\n"
        rep += "[OPERATIONS]\n" + "\n".join([f"- {o}" for o in operational]) + "\n\n"
        rep += "[RISK]\n" + "\n".join([f"- {r}" for r in risk])
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Summary Intelligence Report", 0)
        for title, dataset in [("Financial Index", financial), ("Operations Index", operational), ("Risk Assessment", risk)]:
            doc.add_heading(title, level=1)
            for item in dataset: 
                doc.add_paragraph(item, style='List Bullet')
        out = io.BytesIO()
        doc.save(out)
        return out.getvalue()
    else:
        out = io.BytesIO()
        p_doc = SimpleDocTemplate(out, pagesize=letter, title="Review")
        stls = getSampleStyleSheet()
        ctx = [Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls['Title']), Spacer(1, 15)]
        for h, c, l in [("Financial Metrics", "#1e3a8a", financial), ("Operational Directives", "#1e3a8a", operational), ("Critical Risks", "#7f1d1d", risk)]:
            ctx.append(Paragraph(f"<font size=14 color='{c}'><b>{h}</b></font>", stls['Heading2']))
            for item in l: 
                ctx.append(Paragraph(f"• {item}", stls['Normal']))
            ctx.append(Spacer(1, 10))
        p_doc.build(ctx)
        return out.getvalue()

st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
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
                if e == "pdf": return "".join([p.extract_text() or "" for p in PdfReader(f_obj).pages])
                if e == "docx": return docx2txt.process(f_obj)
                if e == "txt": return f_obj.read().decode("utf-8")
                return ""
            
            if ext == "zip":
                with zipfile.ZipFile(uploaded_file) as z:
                    for info in z.infolist():
                        if not info.filename.startswith('__MACOSX/') and not info.is_dir():
                            inner_ext = info.filename.split(".")[-1].lower()
                            with z.open(info) as f: 
                                txt += extract(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext) + "\n"
            else:
                txt = extract(uploaded_file, ext)
                
            if txt.strip():
                sentences = re.split(r'(?<=[\.!?])\s+', txt)
                st.session_state.fin = list(set([s.strip() for s in sentences if any(k in s.lower() for k in ["$", "revenue", "profit", "expenditure", "cost", "margin", "penalty"]) and len(s.strip()) > 15]))[:5]
                st.session_state.rsk = list(set([s.strip() for s in sentences if any(k in s.lower() for k in ["liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty"]) and len(s.strip()) > 15]))[:5]
                st.session_state.ops = list(set([s.strip() for s in sentences if any(k in s.lower() for k in ["protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub"]) and len(s.strip()) > 15]))[:5]
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
        st.subheader("📋 Executive Intelligence Summary")
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
