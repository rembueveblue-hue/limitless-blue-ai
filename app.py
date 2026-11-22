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
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    h1 { color: #4e8cff; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h3 { color: var(--text-color); font-weight: 400; opacity: 0.8; }
    h4 { color: var(--text-color); border-bottom: 2px solid #1d4ed8; padding-bottom: 6px; margin-top: 15px; }
    .stButton>button { background-color: #1d4ed8; color: white; border-radius: 6px; width: 100%; height: 45px; font-weight: bold; border: none; }
    .metric-box { padding: 14px; background-color: rgba(78, 140, 255, 0.12); color: var(--text-color); border-radius: 8px; margin: 10px 0; border-left: 4px solid #4e8cff; font-size: 14px; line-height: 1.6; }
    .risk-box { padding: 14px; background-color: rgba(239, 68, 68, 0.12); color: var(--text-color); border-radius: 8px; margin: 10px 0; border-left: 4px solid #ef4444; font-size: 14px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# Isolated data compilation engine prevents document generation faults on web links
def build_report(fmt, name, fin_data, ops_data, rsk_data):
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE RECAP:\n{name.upper()}\n" + "="*50 + "\n\n"
        rep += "[FINANCIAL & COMMERCIAL METRICS]\n" + "\n".join(f"- {f}" for f in fin_data) + "\n\n"
        rep += "[OPERATIONAL & CLINICAL DIRECTIVES]\n" + "\n".join(f"- {o}" for o in ops_data) + "\n\n"
        rep += "[CRITICAL LIABILITIES & RISKS]\n" + "\n".join(f"- {r}" for r in rsk_data)
        return rep.encode('utf-8')
    elif "docx" in fmt:
        doc = Document()
        doc.add_heading("Summary Intelligence Report", 0)
        for title, dataset in (("Financial & Commercial Metrics", fin_data), ("Operational & Clinical Directives", ops_data), ("Liabilities, Exclusions & Risk Assessment", rsk_data)):
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
        ctx = list((Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls.byName.get('Title')), Spacer(1, 15)))
        for h, c, l in (("Financial & Commercial Metrics", "#1e3a8a", fin_data), ("Operational & Clinical Directives", "#1e3a8a", ops_data), ("Liabilities, Exclusions & Risk Assessment", "#7f1d1d", rsk_data)):
            ctx.append(Paragraph(f"<font size=14 color='{c}'><b>{h}</b></font>", stls.byName.get('Heading2')))
            for item in l:
                ctx.append(Paragraph(f"• {item}", stls.byName.get('Normal')))
            ctx.append(Spacer(1, 10))
        p_doc.build(ctx)
        return out.getvalue()

st.markdown("# 🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate and legal compliance evaluation.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP)", type=list(("pdf", "docx", "txt", "zip")))

# Persistent state initialization ensures steady execution loops across user selections
if "fin" not in st.session_state:
    st.session_state.fin = list()
    st.session_state.ops = list()
    st.session_state.rsk = list()
    st.session_state.active_fn = None

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        txt, ext = "", uploaded_file.name.split(".").pop().lower()
        try:
            def extract(f_obj, e):
                if e == "pdf":
                    return "".join(p.extract_text() or "" for p in PdfReader(f_obj).pages)
                if e == "docx":
                    return docx2txt.process(f_obj)
                if e == "txt":
                    return f_obj.read().decode("utf-8")
                return ""
            
            if ext == "zip":
                with zipfile.ZipFile(uploaded_file) as z:
                    for info in z.infolist():
                        if not info.filename.startswith('__MACOSX/') and not info.is_dir():
                            inner_ext = info.filename.split(".").pop().lower()
                            with z.open(info) as f:
                                txt += extract(io.BytesIO(f.read()) if inner_ext != "txt" else f, inner_ext) + "\n"
            else:
                txt = extract(uploaded_file, ext)
                
            if txt.strip():
                sentences = re.split(r'(?<=[\.!?])\s+', txt)
                k1 = ("$", "zar", "r ", "revenue", "profit", "expenditure", "cost", "margin", "budget", "fee", "tariff", "limit", "co-payment", "benefit", "premium", "rent", "levy", "valuation", "sla", "%")
                k2 = ("protocol", "tenet", "must", "extract", "auth", "authorization", "step", "schedul", "scrub", "mandatory", "rule", "shall", "notice", "deliverable", "pmb", "treatment", "zoning", "transfer", "pipeline", "schema")
                k3 = ("liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty", "exclusion", "waiting period", "rejection", "indemnit", "termination", "arbitration", "default", "encumbrance", "forfeiture", "vulnerabilit", "downtime")

                st.session_state.fin = list(set(s.strip() for s in sentences if any(k in s.lower() for k in k1) and len(s.strip()) > 15))[:5]
                st.session_state.ops = list(set(s.strip() for s in sentences if any(k in s.lower() for k in k2) and len(s.strip()) > 15))[:5]
                st.session_state.rsk = list(set(s.strip() for s in sentences if any(k in s.lower() for k in k3) and len(s.strip()) > 15))[:5]
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
            st.markdown("#### Financial & Commercial Metrics")
            for i in st.session_state.fin:
                st.markdown(f"<div class='metric-box'><b>[METRIC]</b> {i}</div>", unsafe_allow_html=True)
            st.markdown("#### Operational & Clinical Directives")
            for i in st.session_state.ops:
                st.markdown(f"<div class='metric-box'><b>[DIRECTIVE]</b> {i}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("#### Legal Liabilities & Risk Assessment")
            for i in st.session_state.rsk:
                st.markdown(f"<div class='risk-box'><b>[CRITICAL RISK]</b> {i}</div>", unsafe_allow_html=True)
            
        st.bar_chart(pd.DataFrame({"Metrics": list(("Metrics", "Directives", "Risks")), "Count": list((len(st.session_state.fin), len(st.session_state.ops), len(st.session_state.rsk)))}), x="Metrics", y="Count", use_container_width=True)
        st.markdown("---")
        
        st.subheader("📥 Export Intelligence Report Hub")
        fmt = st.selectbox("Select Export Format Preference:", list(("Portable Document Format (.pdf)", "Microsoft Word (.docx)", "Plain Text Document (.txt)")))
        ext_m = "pdf" if "pdf" in fmt else "docx" if "docx" in fmt else "txt"
        
        st.download_button(
            label=f"📥 Download Summary Report (.{ext_m})", 
            data=build_report(ext_m, uploaded_file.name, st.session_state.fin, st.session_state.ops, st.session_state.rsk), 
            file_name=f"Intel_Report_{uploaded_file.name}.{ext_m}", 
            mime=f"application/{ext_m}" if ext_m != "txt" else "text/plain"
        )
else:
    st.session_state.fin, st.session_state.ops, st.session_state.rsk, st.session_state.active_fn = list(), list(), list(), None
