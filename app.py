import streamlit as st
import docx
import re
import io
import zipfile
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Auto-detect whichever PDF engine is installed on Streamlit Cloud
PDF_ENGINE = None
try:
    import pypdf
    PDF_ENGINE = "pypdf"
except ImportError:
    try:
        import PyPDF2
        PDF_ENGINE = "PyPDF2"
    except ImportError:
        try:
            import fitz
            PDF_ENGINE = "fitz"
        except ImportError:
            PDF_ENGINE = None

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="LIMITLESS BLUE | Enterprise Document Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CLEAN DARK-MODE UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .brand-title { font-size: 2.3rem; font-weight: 800; color: #ffffff; margin-bottom: 0.2rem; }
    .brand-accent { color: #38bdf8; }
    .brand-sub { color: #94a3b8; font-size: 1.0rem; margin-bottom: 1.4rem; }
    
    .domain-badge {
        display: inline-block;
        background-color: #1e293b;
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .metric-box {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 1.05rem;
        border-radius: 6px;
        margin-bottom: 0.85rem;
        line-height: 1.5;
    }
    .directive-box {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-left: 4px solid #10b981;
        padding: 1.05rem;
        border-radius: 6px;
        margin-bottom: 0.85rem;
        line-height: 1.5;
    }
    .risk-box {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-left: 4px solid #f43f5e;
        padding: 1.05rem;
        border-radius: 6px;
        margin-bottom: 0.85rem;
        line-height: 1.5;
    }
    .src-label { color: #94a3b8; font-size: 0.78rem; margin-top: 0.4rem; display: block; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ADAPTIVE DOMAIN LENSES ---
DOMAIN_PROFILES = {
    "Healthcare & Medical Aid": {
        "detect": ("patient", "diagnosis", "clinical", "medical aid", "scheme", "tariff", "co-payment", "pmb", "authorization", "hospital", "claim"),
        "p1_title": "Benefit Limits, Tariffs & Co-Payments",
        "p1_keys": ("tariff", "limit", "co-payment", "levy", "reimbursement", "benefit", "premium", "contribution", "cost", "%", "$", "zar"),
        "p2_title": "Clinical & Pre-Authorization Protocols",
        "p2_keys": ("protocol", "authorization", "pre-auth", "pmb", "referral", "dosage", "treatment", "guideline", "mandatory", "rule"),
        "p3_title": "Exclusions & Compliance Risks",
        "p3_keys": ("exclusion", "waiting period", "penalty", "rejection", "breach", "liability", "non-compliance", "fraud", "dispute"),
        "summary": "Adaptive healthcare synthesis isolates scheme benefit limits, clinical pre-authorization protocols, and policy exclusion risks."
    },
    "Legal & Regulatory Contracts": {
        "detect": ("plaintiff", "defendant", "clause", "indemnity", "jurisdiction", "arbitration", "hereby", "termination", "nda", "agreement", "statute"),
        "p1_title": "Commercial Stakes, Fees & Liability Caps",
        "p1_keys": ("fee", "retainer", "damages", "cap", "settlement", "compensation", "royalty", "invoice", "payment", "%", "$", "zar"),
        "p2_title": "Binding Obligations & Deadlines",
        "p2_keys": ("shall", "notice", "deliverable", "days", "governing law", "jurisdiction", "obligation", "schedule", "mandatory"),
        "p3_title": "Indemnity, Breach & Termination Traps",
        "p3_keys": ("indemnity", "breach", "termination", "arbitration", "nda", "liability", "default", "penalty", "dispute"),
        "summary": "Adaptive legal synthesis isolates commercial fee exposures, binding contractual deadlines, and indemnity or termination traps."
    },
    "Real Estate & Property": {
        "detect": ("lease", "tenant", "landlord", "escrow", "deed", "zoning", "valuation", "mortgage", "erf", "sectional title", "occupation", "premises"),
        "p1_title": "Valuations, Rentals & Levies",
        "p1_keys": ("valuation", "rent", "rental", "levy", "deposit", "yield", "escalation", "rates", "purchase price", "%", "$", "zar"),
        "p2_title": "Lease & Transfer Conditions",
        "p2_keys": ("occupation", "inspection", "zoning", "maintenance", "notice", "transfer", "handover", "renewal", "mandatory"),
        "p3_title": "Title, Zoning & Default Risks",
        "p3_keys": ("encumbrance", "default", "forfeiture", "structural", "compliance", "eviction", "breach", "defect", "penalty"),
        "summary": "Adaptive property synthesis isolates rental/valuation figures, transfer obligations, and title or default risks."
    },
    "Enterprise Systems & Engineering": {
        "detect": ("architecture", "pipeline", "api", "latency", "schema", "sap", "datasphere", "deployment", "server", "specification", "integration"),
        "p1_title": "Resource Budgets & SLA Metrics",
        "p1_keys": ("sla", "uptime", "latency", "throughput", "budget", "license", "cost", "capacity", "gb", "tb", "%", "$", "zar"),
        "p2_title": "Architecture & Deployment Mandates",
        "p2_keys": ("protocol", "pipeline", "schema", "integration", "authentication", "encryption", "schedule", "workflow", "mandatory"),
        "p3_title": "Security & Bottleneck Risks",
        "p3_keys": ("vulnerability", "downtime", "bottleneck", "failure", "breach", "compliance", "timeout", "risk", "loss"),
        "summary": "Adaptive systems synthesis isolates SLA/capacity benchmarks, integration mandates, and bottleneck or security risks."
    },
    "Corporate Finance & Operations": {
        "detect": ("revenue", "ebitda", "profit", "margin", "audit", "expenditure", "shareholder", "balance sheet", "cash flow", "fiscal", "kpi"),
        "p1_title": "Financial Metrics",
        "p1_keys": ("revenue", "profit", "margin", "expenditure", "ebitda", "cash flow", "budget", "roi", "valuation", "%", "$", "zar"),
        "p2_title": "Operational Directives",
        "p2_keys": ("protocol", "rule", "schedule", "mandatory", "step", "policy", "governance", "audit", "target"),
        "p3_title": "Critical Risks",
        "p3_keys": ("liability", "breach", "damage", "nda", "compliance", "penalty", "exposure", "deficit", "loss"),
        "summary": "Executive synthesis confirms core financial structures, mandatory operational protocols, and potential compliance liabilities."
    }
}

# --- 4. UNIVERSAL IN-MEMORY EXTRACTION ENGINE ---
def read_single_file(file_bytes, filename):
    ext = filename.split('.').pop().lower()
    short_name = filename.split('/').pop()
    chunks = list()

    if ext == "pdf":
        if PDF_ENGINE == "pypdf":
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page_num, page in enumerate(reader.pages, start=1):
                txt = page.extract_text()
                if txt and txt.strip():
                    chunks.append((txt, f"{short_name} | Page {page_num}"))
        elif PDF_ENGINE == "PyPDF2":
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page_num, page in enumerate(reader.pages, start=1):
                txt = page.extract_text()
                if txt and txt.strip():
                    chunks.append((txt, f"{short_name} | Page {page_num}"))
        elif PDF_ENGINE == "fitz":
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num, page in enumerate(doc, start=1):
                txt = page.get_text()
                if txt and txt.strip():
                    chunks.append((txt, f"{short_name} | Page {page_num}"))

    elif ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        body_text = ""
        for p in doc.paragraphs:
            if p.text.strip():
                body_text += p.text.strip() + "\n"
        for table in doc.tables:
            for row in table.rows:
                row_text = " - ".join(c.text.strip() for c in row.cells if c.text.strip())
                if row_text:
                    body_text += row_text + ".\n"
        if body_text.strip():
            chunks.append((body_text, short_name))

    elif ext == "txt":
        txt = file_bytes.decode("utf-8", errors="ignore")
        if txt.strip():
            chunks.append((txt, short_name))

    return chunks

def extract_all(uploaded_file):
    raw_bytes = uploaded_file.read()
    ext = uploaded_file.name.split('.').pop().lower()
    all_chunks = list()
    file_count = 0

    if ext == "zip":
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
            for name in z.namelist():
                if not name.endswith('/') and not name.startswith('__MACOSX'):
                    try:
                        file_chunks = read_single_file(z.read(name), name)
                        if file_chunks:
                            all_chunks.extend(file_chunks)
                            file_count += 1
                    except Exception:
                        pass
    else:
        try:
            all_chunks = read_single_file(raw_bytes, uploaded_file.name)
            file_count = 1
        except Exception:
            pass

    return all_chunks, file_count

def detect_domain(full_text):
    lower = full_text.lower()
    best_domain = "Corporate Finance & Operations"
    best_score = 0
    for domain, cfg in DOMAIN_PROFILES.items():
