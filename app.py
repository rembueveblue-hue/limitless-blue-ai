import streamlit as st
import openai
import docx2txt
import pypdf
from fpdf import FPDF
import io

# Page Configuration for the Live Link
st.set_page_config(
    page_title="Limitless Blue AI | Document Intelligence Link", 
    layout="wide", 
    page_icon="🔷",
    initial_sidebar_state="collapsed"
)

# Custom Corporate CSS Injection for Premium UI/UX Styling
st.markdown("""
    <style>
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            h1 { font-size: 1.8rem !important; }
            h3 { font-size: 1.3rem !important; }
            div[data-testid="stFileUploader"] { width: 100% !important; }
        }
        @media (min-width: 769px) {
            .main .block-container {
                max-width: 1200px;
                margin: 0 auto;
                padding-top: 3rem !important;
            }
        }
        div.stButton > button:first-child {
            width: 100%;
            background-color: #1E3A8A;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1rem;
            border: none;
            transition: all 0.2s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #1D4ED8;
            border: none;
        }
    </style>
""", unsafe_allow_html=True
)

st.title("🔷 Limitless Blue | Enterprise Document Intelligence Engine")
st.subheader("Instantly parse corporate and legal data into high-priority executive summaries.")

# Capture the API key passed via the web browser URL (?key=sk-...)
url_params = st.query_params
passed_key = url_params.get("key", "").strip()

# Sidebar Configuration (Collapsible Authentication Management)
st.sidebar.header("🔑 Authentication")
if passed_key:
    api_key = passed_key
    st.sidebar.success("🔒 Authenticated via Secure Link")
else:
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.markdown("---")
uploaded_file = st.file_uploader("Upload Corporate File (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

# Fast, fail-proof multi-document extraction pipeline
def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    if ext == "txt":
        return file.read().decode("utf-8", errors="ignore")
    elif ext == "docx":
        return docx2txt.process(io.BytesIO(file.read()))
    elif ext == "pdf":
        reader = pypdf.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    return ""

# PDF Generation Engine using FPDF2
def generate_pdf_bytes(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, text="Limitless Blue AI - Executive Brief", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=11)
    clean_text = text_content.replace("**", "").replace("###", "").replace("- ", "• ")
    
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 7, text=line)
        
    return pdf.output()

# Execution Logic Blocks
if uploaded_file:
    st.info(f"📁 Loaded: {uploaded_file.name}")
    
    if st.button("🚀 Analyze Document"):
        if not api_key:
            st.error("❌ Please enter your OpenAI API key or use an authorized link to proceed.")
        else:
            with st.spinner("Parsing document and extracting intelligence..."):
                try:
                    document_text = extract_text(uploaded_file)
                    
                    if not document_text.strip():
                        st.error("❌ The uploaded document seems to be empty or unreadable.")
                    else:
                        client = openai.OpenAI(api_key=api_key)
                        
                        master_system_prompt = (
                            "You are an elite Corporate Strategy and Legal Analytics AI. Your job is to instantly parse "
                            "high-volume, unorganized corporate documents and legal files, eliminate the noise, and extract "
                            "high-priority, actionable intelligence.\n\n"
                            "When a document is uploaded, execute the following steps:\n"
                            "- COMPLIANCE & RISK AUDIT: Identify any hidden legal liabilities, contract loopholes, expired clauses, or financial red flags immediately.\n"
                            "- CRITICAL CORE DATA: Extract key entities, specific monetary values, critical deadlines, jurisdiction details, and binding obligations.\n"
                            "- EXECUTIVE SUMMARIZATION: Strip out all boilerplate legal jargon. Rewrite the core meaning into short, punchy, non-technical bullet points accessible to a CEO or senior partner.\n"
                            "- ACTIONABLE NEXT STEPS: Generate a 'High-Priority Action List' detailing exactly what needs immediate attention.\n\n"
                            "OUTPUT FORMAT: Generate the response strictly as a structured, professional executive brief using markdown headers, bold visual anchors for key metrics, and bullet points."
                        )
                        
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": master_system_prompt},
                                {"role": "user", "content": f"Analyze this text block:\n\n{document_text}"}
                            ],
                            temperature=0.3
                        )
                        
                        analysis_result = response.choices.message.content
                        st.session_state["analysis_result"] = analysis_result
                        
                except Exception as e:
                    st.error(f"❌ An error occurred during processing: {str(e)}")

if "analysis_result" in st.session_state:
    st.markdown("### 📑 Executive Intelligence Brief")
    st.markdown(st.session_state["analysis_result"])
    
    try:
        pdf_data = generate_pdf_bytes(st.session_state["analysis_result"])
        st.download_button(
            label="📥 Download Summary as PDF",
            data=pdf_data,
            file_name="Limitless_Blue_Executive_Brief.pdf",
            mime="application/pdf"
        )
    except Exception as pdf_error:
        st.warning(f"Unable to render structural downloadable PDF copy dynamically: {str(pdf_error)}")
