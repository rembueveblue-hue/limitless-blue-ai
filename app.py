import streamlit as st
import pypdf
import docx
import re
import io
import zipfile
import html
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="LIMITLESS BLUE | Enterprise Document Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. EXOTIC CHASSIS & EXECUTIVE COCKPIT UI ---
st.markdown("""
    <style>
    .stApp { background-color: #070b14; color: #f1f5f9; }
    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 1rem;
        margin-bottom: 1.4rem;
    }
    .brand-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.6px;
        color: #ffffff;
        margin: 0;
    }
    .brand-accent { color: #38bdf8; }
    .brand-sub { color: #94a3b8; font-size: 0.98rem; margin-top: 0.2rem; }
    
    .security-pill {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .domain-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    .exec-brief {
        background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 1.25rem 1.4rem;
        border-radius: 8px;
        margin-bottom: 1.25rem;
        line-height: 1.65;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }

    .kpi-card {
        background: linear-gradient(180deg, #111827 0%, #0d1320 100%);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.95rem 1.1rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
    }
    .kpi-label { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.6px; }
    .kpi-val { color: #ffffff; font-size: 1.5rem; font-weight: 800; margin-top: 3px; }

    .pillar-meta {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: -0.4rem;
        margin-bottom: 0.8rem;
    }

    .card-box {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 1.1rem;
        border-radius: 8px;
        margin-bottom: 0.9rem;
        line-height: 1.58;
        font-size: 0.93rem;
        box-shadow: 0 3px 14px rgba(0, 0, 0, 0.25);
    }
    .border-p1 { border-left: 4px solid #38bdf8; }
    .border-p2 { border-left: 4px solid #10b981; }
    .border-p3 { border-left: 4px solid #f43f5e; }

    .source-tag {
        display: inline-block;
        margin-top: 0.6rem;
        background-color: #1e293b;
        color: #cbd5e1;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 4px;
    }
    .hl-num { color: #38bdf8; font-weight: 700; }
    .hl-risk { color: #fb7185; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ADAPTIVE GEARBOX (DOMAIN LENSES) ---
DOMAIN_PROFILES = {
    "Healthcare & Medical Aid": {
        "detect_words": ["patient", "diagnosis", "clinical", "medical aid", "scheme", "tariff", "co-payment", "pmb", "authorization", "icd-10", "hospital", "formulary", "claim"],
        "p1_title": "Benefit Limits, Tariffs & Co-Payments",
        "p1_keys": ["tariff", "limit", "co-payment", "levy", "reimbursement", "benefit", "premium", "contribution", "cost", "%", "$", "zar"],
        "p2_title": "Clinical & Pre-Authorization Protocols",
        "p2_keys": ["protocol", "authorization", "pre-auth", "pmb", "referral", "dosage", "treatment", "guideline", "procedure", "mandatory", "rule"],
        "p3_title": "Exclusions, Waiting Periods & Compliance Risks",
        "p3_keys": ["exclusion", "waiting period", "penalty", "rejection", "breach", "liability", "non-compliance", "fraud", "dispute", "forfeit"],
        "focus": "scheme benefit caps, pre-authorization mandates, and policy exclusions"
    },
    "Legal & Regulatory Contracts": {
        "detect_words": ["plaintiff", "defendant", "clause", "indemnity", "jurisdiction", "arbitration", "hereby", "termination", "nda", "agreement", "witness", "statute", "affidavit"],
        "p1_title": "Commercial Stakes, Fees & Liability Caps",
        "p1_keys": ["fee", "retainer", "damages", "cap", "settlement", "compensation", "royalty", "invoice", "payment", "%", "$", "zar"],
        "p2_title": "Binding Obligations, Notices & Deadlines",
        "p2_keys": ["shall", "notice", "deliverable", "days", "governing law", "jurisdiction", "execute", "obligation", "schedule", "mandatory"],
        "p3_title": "Indemnity, Breach & Termination Traps",
        "p3_keys": ["indemnity", "breach", "termination", "arbitration", "nda", "liability", "default", "penalty", "infringement", "dispute"],
        "focus": "commercial fee exposures, binding contractual deadlines, and indemnity/termination traps"
    },
    "Real Estate & Property": {
        "detect_words": ["lease", "tenant", "landlord", "escrow", "deed", "zoning", "valuation", "mortgage", "erf", "sectional title", "body corporate", "occupation", "premises"],
        "p1_title": "Valuations, Rentals, Levies & Yields",
        "p1_keys": ["valuation", "rent", "rental", "levy", "deposit", "yield", "escalation", "rates", "purchase price", "%", "$", "zar"],
        "p2_title": "Lease, Occupation & Transfer Conditions",
        "p2_keys": ["occupation", "inspection", "zoning", "maintenance", "notice", "transfer", "handover", "renewal", "municipal", "mandatory"],
        "p3_title": "Title, Zoning & Default Exposures",
        "p3_keys": ["encumbrance", "default", "forfeiture", "structural", "compliance", "eviction", "breach", "defect", "servitude", "penalty"],
        "focus": "rental/valuation figures, transfer and maintenance obligations, and title or default risks"
    },
    "Enterprise Systems & Engineering": {
        "detect_words": ["architecture", "pipeline", "api", "latency", "schema", "sap", "datasphere", "deployment", "server", "bandwidth", "specification", "integration", "database"],
        "p1_title": "Resource Budgets, SLAs & Capacity Metrics",
        "p1_keys": ["sla", "uptime", "latency", "throughput", "budget", "license", "cost", "capacity", "gb", "tb", "%", "$", "zar"],
        "p2_title": "System Architecture & Deployment Mandates",
        "p2_keys": ["protocol", "pipeline", "schema", "integration", "authentication", "encryption", "schedule", "workflow", "mandatory", "step"],
        "p3_title": "Security, Downtime & Bottleneck Risks",
        "p3_keys": ["vulnerability", "downtime", "bottleneck", "failure", "breach", "compliance", "deprecated", "timeout", "risk", "loss"],
        "focus": "SLA/capacity benchmarks, core integration mandates, and architectural bottleneck or security risks"
    },
    "Corporate Finance & Operations": {
        "detect_words": ["revenue", "ebitda", "profit", "margin", "audit", "expenditure", "shareholder", "balance sheet", "cash flow", "fiscal", "quarterly", "kpi"],
        "p1_title": "Financial Metrics & Capital Allocation",
        "p1_keys": ["revenue", "profit", "margin", "expenditure", "ebitda", "cash flow", "budget", "roi", "valuation", "%", "$", "zar"],
        "p2_title": "Operational Directives & Governance",
        "p2_keys": ["protocol", "rule", "schedule", "mandatory", "step", "policy", "governance", "audit", "target", "timeline"],
        "p3_title": "Critical Liabilities & Compliance Risks",
        "p3_keys": ["liability", "breach", "damage", "nda", "compliance", "penalty", "exposure", "deficit", "loss", "fraud"],
        "focus": "core financial performance drivers, mandatory operational governance, and critical compliance liabilities"
    }
}

# --- 4. CORE ENGINE BLOCK (100% IN-MEMORY RAM + TABLE EXTRACTION) ---
def extract_segments_from_bytes(file_bytes, filename):
    ext = filename.split('.')[-1].lower()
    segments = []
    short_name = filename.split('/')[-1]
    scanned_pages = 0
    try:
        if ext == "pdf":
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for idx, page in enumerate(reader.pages, start=1):
                extracted = page.extract_text()
                if extracted and extracted.strip():
                    segments.append({
                        "text": extracted,
                        "source": f"{short_name} | Page {idx}"
                    })
                else:
                    scanned_pages += 1
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            para_lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            if para_lines:
                segments.append({
                    "text": "\n".join(para_lines),
                    "source": f"{short_name} | Body Text"
                })
            # Extract structured Word tables (tariffs, pricing, SLAs, schedules)
            for t_idx, table in enumerate(doc.tables, start=1):
                row_sentences = []
                for row in table.rows:
                    cells = [c.text.strip().replace("\n", " ") for c in row.cells if c.text.strip()]
                    if len(cells) >= 2:
