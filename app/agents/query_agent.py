"""
query_agent.py
──────────────────────────────────────────────────────────────
Query Understanding Agent

Responsibilities:
- Cleans and normalises raw user input
- Detects audit intent category (access, data, availability, etc.)
- Enriches the query with domain context before passing to retrieval
- Returns a structured query object consumed by the retrieval agent
──────────────────────────────────────────────────────────────
"""

import re
from dataclasses import dataclass
from typing import Optional


# ── Intent category definitions ──────────────────────────────

INTENT_MAP = {
    "access_control": [
        "access", "login", "authentication", "authorisation", "authorization",
        "permission", "privilege", "role", "user", "identity", "iam",
        "credential", "password", "mfa", "multi-factor", "sso"
    ],
    "data_protection": [
        "data", "encryption", "encrypt", "sensitive", "confidential",
        "pii", "personal", "storage", "transit", "rest", "backup",
        "retention", "deletion", "classification"
    ],
    "availability": [
        "availability", "uptime", "downtime", "disaster", "recovery",
        "backup", "failover", "resilience", "continuity", "outage", "sla"
    ],
    "monitoring_logging": [
        "log", "monitor", "alert", "detect", "siem", "audit trail",
        "event", "activity", "anomaly", "incident", "track", "trace"
    ],
    "change_management": [
        "change", "deploy", "deployment", "release", "update", "patch",
        "version", "rollback", "approval", "configuration"
    ],
    "vendor_risk": [
        "vendor", "third-party", "third party", "supplier", "partner",
        "contractor", "outsource", "subprocessor", "due diligence"
    ],
    "risk_management": [
        "risk", "threat", "vulnerability", "assessment", "treatment",
        "mitigation", "exposure", "likelihood", "impact"
    ]
}


@dataclass
class ProcessedQuery:
    raw: str
    cleaned: str
    intent: Optional[str]
    confidence: str          # "high" | "medium" | "low"
    enriched: str            # Query sent to retrieval agent


def detect_intent(text: str) -> tuple[Optional[str], str]:
    """
    Match query text against intent keyword lists.
    Returns (intent_category, confidence_level).
    """
    text_lower = text.lower()
    scores = {}

    for category, keywords in INTENT_MAP.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > 0:
            scores[category] = hits

    if not scores:
        return None, "low"

    top = max(scores, key=scores.get)
    top_score = scores[top]

    confidence = "high" if top_score >= 3 else "medium" if top_score >= 1 else "low"
    return top, confidence


def enrich_query(cleaned: str, intent: Optional[str]) -> str:
    """
    Append domain context to the query to improve embedding alignment
    with control descriptions.
    """
    enrichment_map = {
        "access_control":    "access control identity management authentication authorisation",
        "data_protection":   "data encryption confidentiality sensitive data protection",
        "availability":      "system availability uptime disaster recovery business continuity",
        "monitoring_logging":"security monitoring logging audit trail incident detection",
        "change_management": "change management deployment configuration control approval",
        "vendor_risk":       "third-party vendor risk management due diligence supplier assessment",
        "risk_management":   "risk assessment threat vulnerability mitigation treatment"
    }

    if intent and intent in enrichment_map:
        return f"{cleaned} {enrichment_map[intent]}"
    return cleaned


def clean_query(raw: str) -> str:
    """
    Normalise whitespace, strip special characters unlikely to
    appear in control descriptions.
    """
    text = raw.strip()
    text = re.sub(r"[^\w\s\-\?\'\,\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def process_query(raw_query: str) -> ProcessedQuery:
    """
    Main entry point for the Query Agent.
    Returns a ProcessedQuery dataclass consumed by the retrieval agent.
    """
    cleaned  = clean_query(raw_query)
    intent, confidence = detect_intent(cleaned)
    enriched = enrich_query(cleaned, intent)

    return ProcessedQuery(
        raw=raw_query,
        cleaned=cleaned,
        intent=intent,
        confidence=confidence,
        enriched=enriched
    )


# ── CLI test ──────────────────────────────────────────────────

if __name__ == "__main__":
    samples = [
        "How is sensitive customer data protected at rest?",
        "What controls exist for monitoring system activity?",
        "Who is allowed to access production systems?",
        "What happens if the system goes down unexpectedly?"
    ]

    for q in samples:
        result = process_query(q)
        print(f"\nRaw     : {result.raw}")
        print(f"Intent  : {result.intent} ({result.confidence})")
        print(f"Enriched: {result.enriched}")