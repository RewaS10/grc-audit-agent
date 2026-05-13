import streamlit as st
import pandas as pd
from agents.retrieval_agent import retrieve_controls
from agents.analysis_agent import generate_response

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="GRC Audit Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark Intelligence Theme
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #080C14 !important;
    color: #E2E8F0 !important;
}

.block-container {
    padding: 2.5rem 3.5rem 4rem !important;
    max-width: 1280px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
}

/* ── Typography base ── */
body { font-family: 'Inter', sans-serif; }

/* ── Top rule ── */
.top-rule {
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #F5A623 0%, #E8833A 40%, transparent 100%);
    margin-bottom: 2.5rem;
    border-radius: 2px;
}

/* ── Header ── */
.header-wrap {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 3rem;
    gap: 2rem;
}

.header-left {}

.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,166,35,0.12);
    border: 1px solid rgba(245,166,35,0.3);
    border-radius: 4px;
    padding: 4px 12px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #F5A623;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.header-badge::before {
    content: '';
    width: 6px;
    height: 6px;
    background: #F5A623;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin: 0 0 0.6rem 0;
}

.header-title span {
    color: #F5A623;
}

.header-sub {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 300;
    color: #64748B;
    letter-spacing: 0.02em;
    line-height: 1.6;
    max-width: 480px;
}

.header-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
    padding-top: 8px;
}

.framework-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 3px;
    border: 1px solid;
}

.pill-soc2 {
    color: #38BDF8;
    border-color: rgba(56,189,248,0.25);
    background: rgba(56,189,248,0.06);
}

.pill-iso {
    color: #A78BFA;
    border-color: rgba(167,139,250,0.25);
    background: rgba(167,139,250,0.06);
}

.pill-gdpr {
    color: #34D399;
    border-color: rgba(52,211,153,0.25);
    background: rgba(52,211,153,0.06);
}

/* ── Stat strip ── */
.stat-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #1E293B;
    border: 1px solid #1E293B;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}

.stat-cell {
    background: #0D1320;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
}

.stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #F5A623;
}

.stat-desc {
    font-size: 11px;
    color: #334155;
    font-weight: 300;
}

/* ── Query section ── */
.query-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
}

.stTextInput > div > div {
    background: #0D1320 !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput > div > div:focus-within {
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 3px rgba(245,166,35,0.08) !important;
}

.stTextInput input {
    background: transparent !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    caret-color: #F5A623 !important;
}

.stTextInput input::placeholder {
    color: #334155 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #F5A623 0%, #E8833A 100%) !important;
    color: #080C14 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.04em !important;
    padding: 14px 28px !important;
    width: 100% !important;
    height: auto !important;
    transition: opacity 0.2s ease, transform 0.1s ease !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Divider ── */
.section-divider {
    width: 100%;
    height: 1px;
    background: #1E293B;
    margin: 2.5rem 0;
}

/* ── Report header ── */
.report-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.report-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.01em;
}

.report-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #334155;
    letter-spacing: 0.08em;
}

/* ── Result cards ── */
.result-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}

.result-card {
    background: #0D1320;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
}

.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.card-controls::before { background: linear-gradient(90deg, #F5A623, transparent); }
.card-risks::before    { background: linear-gradient(90deg, #F87171, transparent); }
.card-recs::before     { background: linear-gradient(90deg, #38BDF8, transparent); }
.card-comp::before     { background: linear-gradient(90deg, #34D399, transparent); }

.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}

.card-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

.icon-controls { background: rgba(245,166,35,0.12); }
.icon-risks    { background: rgba(248,113,113,0.12); }
.icon-recs     { background: rgba(56,189,248,0.12); }
.icon-comp     { background: rgba(52,211,153,0.12); }

.card-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748B;
}

.card-count {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #334155;
    margin-left: auto;
}

/* ── Tag items ── */
.tag-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.tag-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.5;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
}

.tag-control {
    background: rgba(245,166,35,0.06);
    border: 1px solid rgba(245,166,35,0.12);
    color: #CBD5E1;
}

.tag-control .tag-dot { color: #F5A623; font-size: 10px; margin-top: 3px; }

.tag-risk {
    background: rgba(248,113,113,0.06);
    border: 1px solid rgba(248,113,113,0.12);
    color: #CBD5E1;
}

.tag-risk .tag-dot { color: #F87171; font-size: 10px; margin-top: 3px; }

.tag-rec {
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.12);
    color: #CBD5E1;
}

.tag-rec .tag-dot { color: #38BDF8; font-size: 10px; margin-top: 3px; }

.tag-comp {
    background: rgba(52,211,153,0.06);
    border: 1px solid rgba(52,211,153,0.12);
    color: #CBD5E1;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
}

.tag-comp .tag-dot { color: #34D399; font-size: 10px; margin-top: 3px; }

/* ── Query echo card ── */
.query-echo {
    background: #0D1320;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
}

.query-echo-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #334155;
    white-space: nowrap;
    flex-shrink: 0;
}

.query-echo-text {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #94A3B8;
    font-style: italic;
}

/* ── Full-width card ── */
.full-card {
    background: #0D1320;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 22px 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #1E293B;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 1rem;
    opacity: 0.3;
}

.empty-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: #1E293B;
    letter-spacing: 0.06em;
}

/* ── Footer ── */
.footer {
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid #0F172A;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.footer-left {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #1E293B;
    letter-spacing: 0.06em;
}

.footer-right {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #1E293B;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown('<div class="top-rule"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="header-wrap">
    <div class="header-left">
        <div class="header-badge">GRC Intelligence Engine · v2.0</div>
        <div class="header-title">Audit <span>Assistant</span></div>
        <div class="header-sub">
            Agentic compliance analysis for SOC 2 and ISO 27001 audit workflows.
            Query → Retrieve → Analyse → Report.
        </div>
    </div>
    <div class="header-right">
        <div class="framework-pill pill-soc2">SOC 2 Type II</div>
        <div class="framework-pill pill-iso">ISO 27001:2022</div>
        <div class="framework-pill pill-gdpr">GDPR</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STAT STRIP
# ─────────────────────────────────────────────

st.markdown("""
<div class="stat-strip">
    <div class="stat-cell">
        <div class="stat-label">Architecture</div>
        <div class="stat-value">3</div>
        <div class="stat-desc">Agentic reasoning layers</div>
    </div>
    <div class="stat-cell">
        <div class="stat-label">Frameworks</div>
        <div class="stat-value">3+</div>
        <div class="stat-desc">SOC 2, ISO 27001, GDPR</div>
    </div>
    <div class="stat-cell">
        <div class="stat-label">Retrieval</div>
        <div class="stat-value">CSV</div>
        <div class="stat-desc">SOC 2 control tracker dataset</div>
    </div>
    <div class="stat-cell">
        <div class="stat-label">Output</div>
        <div class="stat-value">4</div>
        <div class="stat-desc">Structured response fields</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD KNOWLEDGE BASE
# ─────────────────────────────────────────────

df = pd.read_csv("../data/SOC2_tracker - Sheet1.csv")
knowledge_base = df.to_dict(orient="records")

# ─────────────────────────────────────────────
# QUERY INPUT
# ─────────────────────────────────────────────

st.markdown('<div class="query-label">↳ Enter Audit Query</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])

with col_input:
    query = st.text_input(
        label="audit_query",
        label_visibility="collapsed",
        placeholder="e.g.  How is customer data protected at rest and in transit?",
        key="audit_query"
    )

with col_btn:
    run_analysis = st.button("Analyse →")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────

import datetime

if run_analysis and query.strip():

    controls = retrieve_controls(query, knowledge_base)
    response = generate_response(query, controls)

    report_id = f"AUD-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Report header
    st.markdown(f"""
    <div class="report-header">
        <div class="report-title">Audit Analysis Report</div>
        <div class="report-id">{report_id}</div>
    </div>
    """, unsafe_allow_html=True)

    # Query echo
    st.markdown(f"""
    <div class="query-echo">
        <div class="query-echo-label">Query</div>
        <div class="query-echo-text">"{response["query"]}"</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Build tag HTML helpers ──
    def build_tags(items, tag_class, dot_char="◆"):
        if not items:
            return '<div class="tag-item ' + tag_class + '"><span class="tag-dot">' + dot_char + '</span>None identified.</div>'
        html = ""
        for item in items:
            html += f'<div class="tag-item {tag_class}"><span class="tag-dot">{dot_char}</span>{item}</div>'
        return html

    # ── 2×2 Grid: Controls + Risks ──
    controls_html = build_tags(response.get("matched_controls", []), "tag-control")
    risks_html    = build_tags(response.get("risk_analysis", []),    "tag-risk",  "▲")

    st.markdown(f"""
    <div class="result-grid">
        <div class="result-card card-controls">
            <div class="card-header">
                <div class="card-icon icon-controls">🔐</div>
                <div class="card-title">Matched Controls</div>
                <div class="card-count">{len(response.get("matched_controls", []))} found</div>
            </div>
            <div class="tag-list">{controls_html}</div>
        </div>
        <div class="result-card card-risks">
            <div class="card-header">
                <div class="card-icon icon-risks">⚠️</div>
                <div class="card-title">Risk Analysis</div>
                <div class="card-count">{len(response.get("risk_analysis", []))} identified</div>
            </div>
            <div class="tag-list">{risks_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2×2 Grid: Recommendations + Compliance ──
    recs_html  = build_tags(response.get("recommendations", []),   "tag-rec",  "→")
    comp_html  = build_tags(response.get("compliance_mapping", []),"tag-comp", "✓")

    st.markdown(f"""
    <div class="result-grid">
        <div class="result-card card-recs">
            <div class="card-header">
                <div class="card-icon icon-recs">💡</div>
                <div class="card-title">Recommendations</div>
                <div class="card-count">{len(response.get("recommendations", []))} actions</div>
            </div>
            <div class="tag-list">{recs_html}</div>
        </div>
        <div class="result-card card-comp">
            <div class="card-header">
                <div class="card-icon icon-comp">📋</div>
                <div class="card-title">Compliance Mapping</div>
                <div class="card-count">{len(response.get("compliance_mapping", []))} frameworks</div>
            </div>
            <div class="tag-list">{comp_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif run_analysis and not query.strip():
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">⌕</div>
        <div class="empty-text">Enter a query above to run audit analysis.</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🛡</div>
        <div class="empty-text">Awaiting audit query — results will appear here.</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div class="footer">
    <div class="footer-left">GRC AUDIT ASSISTANT · AGENTIC WORKFLOW SIMULATION</div>
    <div class="footer-right">Not for production audit use without domain expert review.</div>
</div>
""", unsafe_allow_html=True)