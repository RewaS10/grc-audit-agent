import os
import sys
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PATH & BACKEND SETUP (Preserved)
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from agents.query_agent import process_query
from agents.retrieval_agent import retrieve_controls
from agents.analysis_agent import generate_response
# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="GRC Intelligence Engine | Enterprise AI",
    layout="wide",
    initial_sidebar_state="expanded"
)
@st.cache_data(show_spinner=False)
def load_knowledge_base():
    csv_path = os.path.join(BASE_DIR, "../data/SOC2_tracker - Sheet1.csv")
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict(orient="records"), len(df)
    except Exception as e:
        st.error(f"Knowledge base failed to load: {e}")
        return [], 0

knowledge_base, kb_size = load_knowledge_base()

# ─────────────────────────────────────────────────────────────────────────────
# MODERN ENTERPRISE DESIGN SYSTEM (CSS)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;800&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --bg-deep: #060910;
        --bg-surface: #0E121B;
        --bg-card: rgba(23, 28, 41, 0.7);
        --accent-amber: #F5A623;
        --accent-blue: #38BDF8;
        --text-main: #E2E8F0;
        --text-dim: #94A3B8;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --glow-amber: rgba(245, 166, 35, 0.15);
    }

    /* Global Overrides */
    .stApp {
        background-color: var(--bg-deep) !important;
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.05) 0%, transparent 25%),
            radial-gradient(circle at 100% 100%, rgba(245, 166, 35, 0.05) 0%, transparent 25%) !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle);
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.02em !important;
    }

    p, span, div {
        font-family: 'Inter', sans-serif;
    }

    .mono {
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 10px;
    }

    /* Header Section */
    .hero-container {
        padding: 2rem 0 3rem 0;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        color: var(--text-dim);
        font-size: 1.1rem;
        max-width: 800px;
        border-left: 2px solid var(--accent-amber);
        padding-left: 1.5rem;
        margin-top: 1rem;
    }

    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        padding: 1.5rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        border-color: rgba(245, 166, 35, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }

    .stat-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: white;
        font-family: 'Syne', sans-serif;
    }

    /* Search/Query Command Center */
    .query-section {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 3rem;
    }

    /* Input Field Styling */
    .stTextInput input {
        background: var(--bg-deep) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        color: white !important;
        font-size: 1.1rem !important;
    }

    .stTextInput input:focus {
        border-color: var(--accent-amber) !important;
        box-shadow: 0 0 15px var(--glow-amber) !important;
    }

    /* Analysis Report Cards */
    .intel-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
    }

    .risk-badge {
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 1rem;
    }

    .risk-critical { background: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid #F87171; }
    .risk-high { background: rgba(251, 146, 60, 0.15); color: #FB923C; border: 1px solid #FB923C; }
    .risk-medium { background: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid #FBBF24; }
    .risk-low { background: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid #34D399; }

    /* Buttons */
    .stButton > button {
        background: var(--accent-amber) !important;
        color: black !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 3.5rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: none !important;
    }

    /* Hide redundant elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
            /* ─────────────────── SIDEBAR RADIO NAV ─────────────────── */

[data-testid="stSidebar"] .stRadio > div{
    gap: 0.5rem;
}

[data-testid="stSidebar"] label{

    background: transparent;

    border: 1px solid transparent;

    padding: 12px 14px;

    border-radius: 10px;

    transition: all .2s ease;

    color: #94A3B8 !important;

    font-weight: 500;

    margin-bottom: 6px;

    cursor: pointer;
}

[data-testid="stSidebar"] label:hover{

    background: rgba(255,255,255,0.03);

    border: 1px solid rgba(255,255,255,0.06);

    color: white !important;
}

[data-testid="stSidebar"] input:checked + div{

    color: #F5A623 !important;

    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0;">
            <h3 style="color: white; margin-bottom: 0.2rem;"> GRC ENGINE</h3>
            <p class="mono" style="color: var(--accent-amber);">Intelligence v2.4.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    nav = st.radio(
    "Navigation",
    [
        "Audit Intelligence",
        "Control Catalog",
        "Evidence Vault",
        "Risk Analytics",
        "System Settings"
    ],
    label_visibility="collapsed"
)

    
    
    st.markdown("""
        <div style="margin-top: 3rem; padding-top: 1rem; width: 100%;">
            <p class="mono" style="color: #475569; margin-bottom: 4px;">System Health</p>
            <div style="height: 4px; width: 100%; background: #1E293B; border-radius: 10px;">
                <div style="height: 100%; width: 92%; background: #34D399; border-radius: 10px;"></div>
            </div>
            <p style="font-size: 11px; color: #64748B; margin-top: 8px;">Retrieval Latency: 142ms</p>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
    <div class="hero-container">
        <p class="mono" style="color: var(--accent-amber); margin-bottom: 1rem;">// SECURITY REASONING ENGINE</p>
        <h1 class="hero-title">Audit Intelligence, <br>Reimagined.</h1>
        <div class="hero-subtitle">
            Enterprise-grade semantic retrieval and multi-agent reasoning for SOC 2, ISO 27001, 
            and NIST CSF compliance. Precision-engineered for auditors and security teams.
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TOP METRICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(f"""
    <div class="metric-grid">
        <div class="stat-card">
            <p class="mono" style="color: var(--text-dim);">Controls Indexed</p>
            <p class="stat-value">{kb_size}</p>
            <p style="color: #34D399; font-size: 12px; margin-top: 4px;">↑ 12.4% vs last audit</p>
        </div>
        <div class="stat-card">
            <p class="mono" style="color: var(--text-dim);">Embedding Model</p>
            <p class="stat-value" style="font-size: 1.2rem; color: var(--accent-blue);">MINILM-L6-V2</p>
            <p style="color: var(--text-dim); font-size: 12px; margin-top: 14px;">Vector Latency: 0.04ms</p>
        </div>
        <div class="stat-card">
            <p class="mono" style="color: var(--text-dim);">Active Frameworks</p>
            <p class="stat-value">4</p>
            <p style="color: var(--text-dim); font-size: 12px; margin-top: 4px;">SOC2, ISO, NIST, GDPR</p>
        </div>
        <div class="stat-card">
            <p class="mono" style="color: var(--text-dim);">Agent Reliability</p>
            <p class="stat-value">99.8%</p>
            <p style="color: #34D399; font-size: 12px; margin-top: 4px;">Reasoning Consensus</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COMMAND CENTER (QUERY INPUT)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="query-section">', unsafe_allow_html=True)
st.markdown('<p class="mono" style="color: var(--accent-amber); margin-bottom: 1rem;">> Input Compliance Query</p>', unsafe_allow_html=True)

q_col1, q_col2 = st.columns([4, 1])

with q_col1:
    query = st.text_input(
        "query",
        label_visibility="collapsed",
        placeholder="e.g., How do we manage encryption keys and production access logs?"
    )
    st.markdown("""
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <span style="font-size: 12px; color: #475569;">Suggestions:</span>
            <span style="font-size: 12px; color: var(--accent-blue); cursor: pointer;">Data at rest policy</span>
            <span style="font-size: 12px; color: var(--accent-blue); cursor: pointer;">MFA requirements</span>
            <span style="font-size: 12px; color: var(--accent-blue); cursor: pointer;">Incident response plan</span>
        </div>
    """, unsafe_allow_html=True)

with q_col2:
    run = st.button("RUN INTELLIGENCE")

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOGIC & RESULTS
# ─────────────────────────────────────────────────────────────────────────────

def get_risk_style(level):
    return f"risk-{level.lower()}"

if run and query.strip():
    with st.status("Initializing Multi-Agent Reasoning...", expanded=True) as status:
        st.write("Fetching semantic embeddings...")
        processed_query = process_query(query)
        st.write("Scanning knowledge base for control matches...")
        controls = retrieve_controls(processed_query, knowledge_base, top_k=5, min_score=0.20)
        st.write("Generating compliance risk profile...")
        report = generate_response(processed_query, controls)
        status.update(label="Analysis Complete", state="complete", expanded=False)

    # Main Intelligence Layout
    st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <h2 style="color: white; margin-bottom: 0.5rem;">Audit Findings Report</h2>
            <div class="risk-badge {get_risk_style(report.risk_level)}">
                Overall Risk Profile: {report.risk_level}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Row 1: Key Analysis
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<p class="mono" style="color: var(--accent-amber);">Matched Control Intelligence</p>', unsafe_allow_html=True)
        for ctrl, score in zip(report.matched_controls, report.similarity_scores):
            pct = int(score * 100)
            st.markdown(f"""
                <div style="margin-bottom: 1.2rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 13px; color: var(--text-main); font-weight: 500;">{ctrl}</span>
                        <span style="font-size: 11px; color: var(--accent-blue);">{pct}% Match</span>
                    </div>
                    <div style="height: 4px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                        <div style="height: 100%; width: {pct}%; background: var(--accent-blue); border-radius: 10px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<p class="mono" style="color: var(--accent-amber);">Risk Reasoning</p>', unsafe_allow_html=True)
        for risk in report.risk_analysis:
            st.markdown(f"""
                <div style="padding: 0.8rem; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 0.5rem; border-left: 3px solid #F87171; font-size: 14px;">
                    {risk}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Actions & Coverage
    st.write("")
    c3, c4 = st.columns([3, 2])

    with c3:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<p class="mono" style="color: var(--accent-amber);">Remediation Roadmap</p>', unsafe_allow_html=True)
        for i, rec in enumerate(report.recommendations):
            st.markdown(f"""
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                    <div style="color: var(--accent-amber); font-weight: 800;">0{i+1}</div>
                    <div style="color: var(--text-main); font-size: 14px;">{rec}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="intel-card">', unsafe_allow_html=True)
        st.markdown('<p class="mono" style="color: var(--accent-amber);">Framework Alignment</p>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, fw in enumerate(report.compliance_mapping):
            target_col = cols[i % 2]
            target_col.markdown(f"""
                <div style="padding: 10px; border: 1px solid var(--border-subtle); border-radius: 4px; text-align: center; font-size: 12px; margin-bottom: 8px;">
                    {fw}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Evidence Section
    if report.evidence_required:
        st.write("")
        st.markdown('<div class="intel-card" style="border-top: 2px solid var(--accent-blue);">', unsafe_allow_html=True)
        st.markdown('<p class="mono" style="color: var(--accent-blue);">Required Evidence for Audit (Artifacts)</p>', unsafe_allow_html=True)
        ev_cols = st.columns(len(report.evidence_required) if len(report.evidence_required) > 0 else 1)
        for i, ev in enumerate(report.evidence_required):
            ev_cols[i % len(ev_cols)].markdown(f"""
                <div style="font-size: 13px; color: var(--text-dim);">
                    • {ev}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif not query.strip() and run:
    st.warning("SYSTEM NOTICE: Query input required for analysis initialization.")
else:
    # Empty State
    st.markdown("""
        <div style="text-align: center; padding: 5rem 0; border: 1px dashed var(--border-subtle); border-radius: 20px;">
            <p style="color: #475569; font-size: 1.2rem;">System Idle. Awaiting Compliance Query...</p>
            <p class="mono" style="color: #1E293B; margin-top: 1rem;">Ready for semantic audit reasoning</p>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
    <div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
        <div class="mono" style="color: #475569;">© 2026 GRC INTELLIGENCE ENGINE // TERMINAL_01</div>
        <div style="display: flex; gap: 2rem;">
            <span class="mono" style="color: #475569;">SECURITY STATUS: ENCRYPTED</span>
            <span class="mono" style="color: #475569;">REGION: US-EAST-1</span>
        </div>
    </div>
""", unsafe_allow_html=True)