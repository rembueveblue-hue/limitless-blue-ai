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

PROFILES = {
    "Corporate Finance & Operations": {
        "detect": ("revenue", "profit", "expenditure", "margin", "ebitda", "audit", "fiscal", "shareholder"),
        "labels": ("Financial Metrics & Performance", "Strategic & Operational Directives", "Legal Liabilities & Risk Assessment"),
        "tags": ("FINANCIAL", "OPERATIONS", "CRITICAL RISK"),
        "p1": ("$", "zar", "revenue", "profit", "expenditure", "cost", "margin", "budget", "fee", "%"),
        "p2": ("protocol", "tenet", "must", "extract", "auth", "step", "schedul", "scrub", "mandatory", "rule"),
        "p3": ("liabilit", "breach", "damages", "nondisclosure", "nda", "comply", "compliance", "restrict", "penalty")
    },
    "Healthcare & Medical Aid": {
        "detect": ("patient", "diagnosis", "clinical", "medical aid", "scheme", "tariff", "co-payment", "pmb", "hospital", "claim"),
        "labels": ("Benefit Limits, Tariffs & Co-Payments", "Clinical & Pre-Authorization Protocols", "Exclusions & Compliance Risks"),
        "tags": ("BENEFIT / TARIFF", "CLINICAL PROTOCOL", "EXCLUSION / RISK"),
        "p1": ("$", "zar", "tariff", "limit", "co-payment", "levy", "benefit", "premium", "contribution", "cost", "%"),
        "p2": ("protocol", "authorization", "pre-auth", "pmb", "referral", "dosage", "treatment", "guideline", "mandatory", "rule"),
        "p3": ("exclusion", "waiting period", "penalty", "rejection", "breach", "liabilit", "compliance", "fraud", "dispute")
    },
    "Legal & Regulatory Contracts": {
        "detect": ("plaintiff", "defendant", "clause", "indemnity", "jurisdiction", "arbitration", "hereby", "termination", "agreement", "statute"),
        "labels": ("Commercial Stakes, Fees & Liability Caps", "Binding Obligations & Deadlines", "Indemnity, Breach & Termination Traps"),
        "tags": ("COMMERCIAL / FEE", "OBLIGATION", "LEGAL TRAP"),
        "p1": ("$", "zar", "fee", "retainer", "damages", "cap", "settlement", "compensation", "invoice", "payment", "%"),
        "p2": ("shall", "notice", "deliverable", "days", "governing law", "jurisdiction", "obligation", "schedul", "mandatory"),
        "p3": ("indemnit", "breach", "termination", "arbitration", "nda", "liabilit", "default", "penalty", "dispute")
    },
    "Real Estate & Property": {
        "detect": ("lease", "tenant", "landlord", "escrow", "deed", "zoning", "valuation", "mortgage", "erf", "sectional title", "premises"),
        "labels": ("Valuations, Rentals & Levies", "Lease & Transfer Conditions", "Title, Zoning & Default Risks"),
        "tags": ("VALUATION / LEVY", "LEASE CONDITION", "PROPERTY RISK"),
        "p1": ("$", "zar", "valuation", "rent", "rental", "levy", "deposit", "yield", "escalation", "rates", "purchase price", "%"),
        "p2": ("occupation", "inspection", "zoning", "maintenance", "notice", "transfer", "handover", "renewal", "mandatory"),
        "p3": ("encumbrance", "default", "forfeiture", "structural", "compliance", "eviction", "breach", "defect", "penalty")
    },
    "Enterprise Systems & Engineering": {
        "detect": ("architecture", "pipeline", "api", "latency", "schema", "sap", "datasphere", "deployment", "server", "specification", "integration"),
        "labels": ("Resource Budgets & SLA Metrics", "Architecture & Deployment Mandates", "Security & Bottleneck Risks"),
        "tags": ("SLA / CAPACITY", "SYSTEM MANDATE", "TECH RISK"),
        "p1": ("$", "zar", "sla", "uptime", "latency", "throughput", "budget", "license", "cost", "capacity", "gb", "tb", "%"),
        "p2": ("protocol", "pipeline", "schema", "integration", "authentication", "encryption", "schedul", "workflow", "mandatory"),
        "p3": ("vulnerabilit", "downtime", "bottleneck", "failure", "breach", "compliance", "timeout", "risk", "loss")
    }
}

def detect_profile(text):
    low = text.lower()
    best_name = "Corporate Finance & Operations"
    best_hits = 0
    for name, cfg in PROFILES.items():
        hits = 0
        for w in cfg.get("detect", ()):
            hits += low.count(w)
        if hits > best_hits:
            best_hits = hits
            best_name = name
    return best_name

def extract_text(raw_bytes, ext):
    if ext == "pdf":
        parts = list()
        reader = PdfReader(io.BytesIO(raw_bytes))
        for p in reader.pages:
            parts.append(p.extract_text() or "")
        return "".join(parts)
    if ext == "docx":
        return docx2txt.process(io.BytesIO(raw_bytes))
    if ext == "txt":
        return raw_bytes.decode("utf-8", errors="ignore")
    return ""

def filter_sentences(sentences, keywords):
    found = list()
    seen = set()
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) > 15 and s_clean not in seen:
            s_low = s_clean.lower()
            for k in keywords:
                if k in s_low:
                    seen.add(s_clean)
                    found.append(s_clean)
                    break
        if len(found) == 5:
            break
    return found

def build_report(fmt, name, labels, tags, p1_data, p2_data, p3_data):
    t1, t2, t3 = tags
    l1, l2, l3 = labels
    if "txt" in fmt:
        rep = f"LIMITLESS BLUE RECAP:\n{name.upper()}\n" + "=" * 50 + "\n\n"
        rep += f"[{t1}]\n" + "\n".join(f"- {f}" for f in p1_data) + "\n\n"
        rep += f"[{t2}]\n" + "\n".join(f"- {o}" for o in p2_data) + "\n\n"
        rep += f"[{t3}]\n" + "\n".join(f"- {r}" for r in p3_data)
        return rep.encode("utf-8")
    if "docx" in fmt:
        doc = Document()
        doc.add_heading("Summary Intelligence Report", 0)
        for title, dataset in ((l1, p1_data), (l2, p2_data), (l3, p3_data)):
            doc.add_heading(title, level=1)
            for item in dataset:
                doc.add_paragraph(item, style="List Bullet")
        out = io.BytesIO()
        doc.save(out)
        return out.getvalue()
    out = io.BytesIO()
    p_doc = SimpleDocTemplate(out, pagesize=letter, title="Review")
    stls = getSampleStyleSheet()
    ctx = list()
    ctx.append(Paragraph("<font size=22 color='#1d4ed8'><b>Limitless Blue Executive Report</b></font>", stls.byName.get("Title")))
    ctx.append(Spacer(1, 15))
    for h, c, l in ((l1, "#1e3a8a", p1_data), (l2, "#1e3a8a", p2_data), (l3, "#7f1d1d", p3_data)):
        ctx.append(Paragraph(f"<font size=14 color='{c}'><b>{h}</b></font>", stls.byName.get("Heading2")))
        for item in l:
            safe_item = item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            ctx.append(Paragraph(f"• {safe_item}", stls.byName.get("Normal")))
        ctx.append(Spacer(1, 10))
    p_doc.build(ctx)
    return out.getvalue()

st.markdown("# 💎 Limitless Blue | Enterprise Document Intelligence Engine")
st.markdown("### Secure, localized data extraction for corporate, medical, property, and legal compliance evaluation.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, TXT, or ZIP)", type=list(("pdf", "docx", "txt", "zip")))

if "fin" not in st.session_state:
    st.session_state.fin = list()
    st.session_state.ops = list()
    st.session_state.rsk = list()
    st.session_state.active_fn = None
    st.session_state.active_profile = "Corporate Finance & Operations"

if uploaded_file:
    if st.session_state.active_fn != uploaded_file.name:
        file_bytes = uploaded_file.getvalue()
        txt = ""
        ext = uploaded_file.name.split(".").pop().lower()
        if ext == "zip":
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                for info in z.infolist():
                    if not info.filename.startswith("__MACOSX/") and not info.is_dir():
                        inner_ext = info.filename.split(".").pop().lower()
                        with z.open(info) as f:
                            txt += extract_text(f.read(), inner_ext) + "\n"
        else:
            txt = extract_text(file_bytes, ext)

        if txt.strip():
            profile_name = detect_profile(txt)
            cfg = PROFILES.get(profile_name)
            sentences = re.split(r'(?<=[\.!?])\s+', txt)

            st.session_state.fin = filter_sentences(sentences, cfg.get("p1"))
            st.session_state.ops = filter_sentences(sentences, cfg.get("p2"))
            st.session_state.rsk = filter_sentences(sentences, cfg.get("p3"))
            st.session_state.active_fn = uploaded_file.name
            st.session_state.active_profile = profile_name
            st.success(f"Successfully analyzed: {uploaded_file.name}  |  {profile_name}")
        else:
            st.warning("No readable text discovered in file contents.")
            st.session_state.active_fn = None

    if st.session_state.active_fn:
