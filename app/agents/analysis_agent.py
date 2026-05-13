"""
analysis_agent.py
──────────────────────────────────────────────────────────────
Compliance Analysis Agent

Responsibilities:
- Processes controls retrieved by the retrieval agent
- Generates risk analysis per control
- Produces actionable recommendations
- Maps controls to applicable compliance frameworks
- Assigns risk severity level (Critical / High / Medium / Low)
- Returns a structured audit response object

Implementation: deterministic rule-based reasoning engine.
Chosen for auditability — reasoning steps are inspectable
and reproducible, which matters in a compliance context
where the tool's own outputs may be subject to review.

LLM integration (Ollama / OpenAI) is the top roadmap item.
──────────────────────────────────────────────────────────────
"""

from dataclasses import dataclass, field
from typing import Optional
import datetime


# ── Risk taxonomy ─────────────────────────────────────────────

RISK_PATTERNS = {
    "Unauthorized access":        ("Critical", "Implement role-based access control (RBAC) and enforce MFA on all privileged accounts."),
    "Data breach":                ("Critical", "Enforce AES-256 encryption at rest and TLS 1.2+ in transit. Conduct quarterly encryption audits."),
    "Undetected incidents":       ("High",     "Deploy SIEM with real-time alerting. Define escalation runbooks and test detection capabilities monthly."),
    "System unavailability":      ("High",     "Establish RTO/RPO targets. Test disaster recovery procedures semi-annually."),
    "Unauthorised changes":       ("High",     "Enforce change approval workflows with peer review and rollback capability."),
    "Third-party exposure":       ("Medium",   "Conduct annual vendor risk assessments. Include security requirements in all supplier contracts."),
    "Compliance gap":             ("Medium",   "Map current controls against framework requirements. Prioritise remediation by risk level."),
    "Insufficient logging":       ("Medium",   "Centralise log collection. Retain logs for minimum 90 days. Define log review frequency."),
    "Weak authentication":        ("High",     "Enforce password complexity policies. Implement MFA. Audit inactive accounts quarterly."),
    "Data retention violation":   ("Medium",   "Define and enforce a data retention and deletion policy aligned with GDPR requirements."),
}

FRAMEWORK_MAP = {
    "ISO 27001": [
        "access", "encryption", "control", "information", "asset",
        "risk", "incident", "continuity", "supplier", "audit",
        "monitoring", "policy", "change", "physical"
    ],
    "SOC 2": [
        "access", "availability", "confidentiality", "monitoring",
        "incident", "change", "encryption", "logging", "processing",
        "backup", "recovery", "security", "authentication"
    ],
    "GDPR": [
        "data", "personal", "pii", "privacy", "retention", "deletion",
        "breach", "consent", "encryption", "transfer", "subject"
    ],
    "NIST CSF": [
        "identify", "protect", "detect", "respond", "recover",
        "risk", "asset", "incident", "monitoring", "vulnerability"
    ]
}

SEVERITY_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


# ── Output dataclass ──────────────────────────────────────────

@dataclass
class AuditReport:
    report_id:          str
    timestamp:          str
    query:              str
    intent:             Optional[str]
    matched_controls:   list[str]
    risk_analysis:      list[str]
    risk_level:         str
    recommendations:    list[str]
    compliance_mapping: list[str]
    evidence_required:  list[str]
    control_owners:     list[str]
    control_statuses:   list[str]
    similarity_scores:  list[float]
    controls_raw:       list[dict] = field(default_factory=list)


# ── Framework detection ───────────────────────────────────────

def _detect_frameworks(controls: list[dict]) -> list[str]:
    """
    Infer applicable compliance frameworks from control content.
    """
    text = " ".join([
        str(c.get("Control Name", "")) + " " +
        str(c.get("Description", "")) + " " +
        str(c.get("Evidence Required", ""))
        for c in controls
    ]).lower()

    matched = []
    for framework, keywords in FRAMEWORK_MAP.items():
        if sum(1 for kw in keywords if kw in text) >= 2:
            matched.append(framework)

    return matched if matched else ["SOC 2"]


# ── Risk inference ────────────────────────────────────────────

def _infer_risks(controls: list[dict]) -> list[tuple[str, str, str]]:
    """
    Returns list of (risk_label, severity, recommendation) tuples.
    """
    combined_text = " ".join([
        str(c.get("Control Name", "")) + " " +
        str(c.get("Description", "")) + " " +
        str(c.get("Risk", ""))
        for c in controls
    ]).lower()

    found = []
    seen  = set()

    for risk_label, (severity, recommendation) in RISK_PATTERNS.items():
        key_words = risk_label.lower().split()
        if any(kw in combined_text for kw in key_words) and risk_label not in seen:
            found.append((risk_label, severity, recommendation))
            seen.add(risk_label)

    # Also pull explicit Risk column if present
    for c in controls:
        raw_risk = str(c.get("Risk", "")).strip()
        if raw_risk and raw_risk not in seen and raw_risk.lower() not in ("nan", ""):
            # Try to match to known pattern
            matched = False
            for risk_label, (severity, recommendation) in RISK_PATTERNS.items():
                if any(kw in raw_risk.lower() for kw in risk_label.lower().split()):
                    found.append((raw_risk, severity, recommendation))
                    matched = True
                    break
            if not matched:
                found.append((raw_risk, "Medium", "Review and remediate this control area as a priority."))
            seen.add(raw_risk)

    return found


# ── Overall severity ──────────────────────────────────────────

def _overall_severity(risk_tuples: list[tuple]) -> str:
    if not risk_tuples:
        return "Low"
    severities = [t[1] for t in risk_tuples]
    return max(severities, key=lambda s: SEVERITY_RANK.get(s, 0))


# ── Main analysis function ────────────────────────────────────

def generate_response(
    processed_query,           # ProcessedQuery | str
    controls: list[dict]
) -> AuditReport:
    """
    Generate a full structured audit report from retrieved controls.

    Parameters
    ----------
    processed_query : ProcessedQuery or str
        Output from query_agent, or raw query string.
    controls : list[dict]
        Controls returned by retrieval_agent (with similarity_score).

    Returns
    -------
    AuditReport dataclass
    """
    # Handle plain string input for backward compatibility
    if isinstance(processed_query, str):
        query_text  = processed_query
        intent      = None
    else:
        query_text  = processed_query.raw
        intent      = processed_query.intent

    now       = datetime.datetime.now()
    report_id = f"AUD-{now.strftime('%Y%m%d-%H%M%S')}"
    timestamp = now.strftime("%d %b %Y, %H:%M:%S UTC")

    if not controls:
        return AuditReport(
            report_id          = report_id,
            timestamp          = timestamp,
            query              = query_text,
            intent             = intent,
            matched_controls   = [],
            risk_analysis      = ["No relevant controls found for this query."],
            risk_level         = "Unknown",
            recommendations    = ["Refine your query or expand the control knowledge base."],
            compliance_mapping = [],
            evidence_required  = [],
            control_owners     = [],
            control_statuses   = [],
            similarity_scores  = [],
            controls_raw       = []
        )

    # Extract structured fields
    matched_controls  = [
        f"[{c.get('Control ID', '?')}] {c.get('Control Name', 'Unknown Control')}"
        for c in controls
    ]
    evidence_required = [
        str(c.get("Evidence Required", "")).strip()
        for c in controls
        if str(c.get("Evidence Required", "")).strip() not in ("", "nan")
    ]
    control_owners    = [
        str(c.get("Owner", "")).strip()
        for c in controls
        if str(c.get("Owner", "")).strip() not in ("", "nan")
    ]
    control_statuses  = [
        f"[{c.get('Control ID','?')}] {c.get('Status','Unknown')}"
        for c in controls
    ]
    similarity_scores = [c.get("similarity_score", 0.0) for c in controls]

    # Risk inference
    risk_tuples        = _infer_risks(controls)
    risk_analysis      = [f"{r[0]} — Severity: {r[1]}" for r in risk_tuples] or ["No critical risks identified."]
    recommendations    = list(dict.fromkeys([r[2] for r in risk_tuples])) or ["Implement and review identified controls on a regular schedule."]
    risk_level         = _overall_severity(risk_tuples)
    compliance_mapping = _detect_frameworks(controls)

    return AuditReport(
        report_id          = report_id,
        timestamp          = timestamp,
        query              = query_text,
        intent             = intent,
        matched_controls   = matched_controls,
        risk_analysis      = risk_analysis,
        risk_level         = risk_level,
        recommendations    = recommendations,
        compliance_mapping = compliance_mapping,
        evidence_required  = evidence_required,
        control_owners     = control_owners,
        control_statuses   = control_statuses,
        similarity_scores  = similarity_scores,
        controls_raw       = controls
    )


# ── CLI test ──────────────────────────────────────────────────

if __name__ == "__main__":
    sample_controls = [
        {
            "Control ID": "CC6.1",
            "Control Name": "Access Control Policy",
            "Description": "Users must have unique IDs and role-based access",
            "Risk": "Unauthorized access",
            "Evidence Required": "Access control policy document, user provisioning logs",
            "Owner": "IT Security",
            "Status": "Implemented",
            "similarity_score": 0.82
        },
        {
            "Control ID": "EN-01",
            "Control Name": "Data Encryption",
            "Description": "Sensitive data must be encrypted at rest and in transit",
            "Risk": "Data breach",
            "Evidence Required": "Encryption configuration, TLS certificate records",
            "Owner": "Engineering",
            "Status": "Implemented",
            "similarity_score": 0.74
        }
    ]

    from agents.query_agent import process_query
    pq     = process_query("How is sensitive data protected?")
    report = generate_response(pq, sample_controls)

    print(f"\nReport ID   : {report.report_id}")
    print(f"Risk Level  : {report.risk_level}")
    print(f"Controls    : {report.matched_controls}")
    print(f"Risks       : {report.risk_analysis}")
    print(f"Frameworks  : {report.compliance_mapping}")
    print(f"Evidence    : {report.evidence_required}")