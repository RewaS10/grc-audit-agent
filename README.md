# GRC Audit Assistant — Agentic Workflow Simulation

A Python-based GRC audit assistant that simulates an agentic reasoning workflow to interpret compliance queries, retrieve relevant security controls, and generate structured audit responses with mapped evidence requirements. Built to reflect real-world audit processes used in compliance platforms operating across frameworks such as SOC 2 and ISO 27001.

---

## Overview

Audit query resolution in GRC workflows is typically manual, inconsistent, and slow. This tool automates the first-response layer of that process — accepting a natural language compliance question, identifying applicable control domains through keyword-based reasoning, and returning a structured, audit-ready response with evidence requirements, risk classification, and ownership details.

The system is implemented as a multi-agent pipeline where each function represents a discrete reasoning step, simulating the interpret → retrieve → respond loop of a human audit analyst.

---

## Agentic Workflow Architecture

```
User Query (Natural Language)
        │
        ▼
┌──────────────────────────┐
│   Query Understanding     │  ← Keyword extraction identifies
│   Agent                   │    relevant control domains
│   extract_keywords()      │    from natural language input
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│   Retrieval Agent         │  ← Matches extracted keywords against
│   retrieve_controls()     │    SOC 2 control knowledge base
│                           │    (hardcoded KB or CSV tracker)
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐
│   Analysis Agent          │  ← Generates structured audit response
│   generate_response()     │    with controls, risks, evidence
│                           │    requirements, and compliance tags
└──────────────────────────┘
        │
        ▼
Structured Audit Response Output
```

---

## Features

- **Natural language query intake** — Accepts plain-language audit questions without requiring structured input format
- **Keyword-based control mapping** — Rule-based reasoning layer extracts intent from queries and maps to relevant control domains
- **Dual knowledge base support** — Works with both a hardcoded control dictionary and a structured `SOC2_tracker.csv` dataset
- **Risk classification** — Automatically assigns risk level (High / Medium) based on identified risk types
- **Evidence requirement mapping** — Outputs specific evidence requirements per control, drawn from the tracker dataset
- **Compliance framework tagging** — Each response includes applicable frameworks (SOC 2, ISO 27001, GDPR)
- **Ownership tracking** — Identifies control owners from the tracker for accountability mapping

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| Data Handling | Pandas |
| Knowledge Base | Hardcoded dictionary + CSV (`SOC2_tracker.csv`) |
| Output Formatting | pprint (structured dict output) |
| Environment | Google Colab |
| Version Control | Git, GitHub |

---

## Controls Coverage

### Hardcoded Knowledge Base (Version 1)

| Control ID | Title | Frameworks |
|---|---|---|
| AC-01 | Access Control Policy | ISO 27001, SOC 2 |
| EN-01 | Data Encryption | ISO 27001, GDPR |
| LG-01 | Logging and Monitoring | SOC 2 |

### CSV-Based Knowledge Base (Version 2)

Loaded dynamically from `SOC2_tracker.csv`. Expected columns:

| Column | Description |
|---|---|
| `Control ID` | Unique control identifier |
| `Control Name` | Short name of the control |
| `Description` | Full control description |
| `Evidence Required` | Specific evidence an auditor would require |
| `Owner` | Team or individual responsible for the control |
| `Status` | Implementation status (e.g., Implemented, In Progress) |

---

## Example

**Input Query:**
```
How is data protected?
```

**Version 1 Output (Hardcoded KB):**
```python
{
  'query': 'How is data protected?',
  'summary': 'Relevant security controls identified based on query.',
  'controls': ['EN-01'],
  'risks': ['Data breach'],
  'risk_level': 'High',
  'recommendation': 'Implement and review the above controls regularly.',
  'compliance': ['ISO 27001', 'GDPR']
}
```

**Version 2 Output (CSV Tracker):**
```python
{
  'query': 'How is data protected?',
  'controls': ['EN-01'],
  'evidence_required': ['Encryption configuration documentation, TLS logs'],
  'owners': ['Security Team'],
  'status': ['Implemented']
}
```

---

## Project Structure

```
grc-audit-assistant/
│
├── GRC_Audit_agent.ipynb     # Main Colab notebook (full workflow)
├── SOC2_tracker.csv          # SOC 2 control dataset (required for Version 2)
└── README.md                 # Project documentation
```

---

## Setup and Usage

### Prerequisites
```
Python 3.8+
Google Colab (recommended) or local Jupyter environment
SOC2_tracker.csv placed in the same directory or mounted drive
```

### Running in Google Colab

1. Upload `GRC_Audit_agent.ipynb` to Google Colab
2. Upload `SOC2_tracker.csv` to the Colab session storage or mount Google Drive
3. Run all cells in sequence
4. Enter your audit query when prompted

### Running Locally

```bash
git clone https://github.com/your-username/grc-audit-assistant.git
cd grc-audit-assistant
pip install pandas
jupyter notebook GRC_Audit_agent.ipynb
```

---

## Design Decisions and Limitations

**Why rule-based keyword extraction instead of an LLM?**
The keyword extraction layer uses deterministic logic intentionally — ensuring predictable, auditable control retrieval without dependence on external API calls or non-deterministic model outputs. This makes the retrieval layer transparent and reproducible, which is a meaningful property in a compliance context where auditability of the tool itself matters.

**Current limitations:**
- Keyword matching is limited to three domains (access, data, log) in Version 1 — expanding the keyword dictionary improves coverage significantly
- The system does not handle compound or ambiguous queries where multiple unrelated control domains are implicated
- Output is structured Python dict format — a production version would serialise to JSON or render to a formatted audit report template

**Potential extensions:**
- Integrate an LLM layer (Claude / OpenAI) for semantic query understanding beyond keyword matching
- Add a confidence score per retrieved control
- Export audit responses to PDF or structured JSON for formal audit documentation workflows
- Expand `SOC2_tracker.csv` to cover full SOC 2 Trust Service Criteria (CC1–CC9, A1, C1, PI1, P1–P8)

---

## Relevance to GRC and Compliance Automation

This project addresses a concrete operational problem in audit workflows: the manual, inconsistent handling of routine compliance queries. The agentic pipeline design — discrete agents for understanding, retrieval, and analysis — mirrors the architecture being adopted in production GRC platforms for automating audit partner query management, evidence collection tracking, and control gap identification.

---

## Author

**Rewa Shukla**
Cybersecurity | GRC | AI-Assisted Audit Workflows
[LinkedIn](https://www.linkedin.com/in/rewa-shukla-320b02301) | rewashukla04@gmail.com

---

*Built as part of an applied GRC learning initiative. Intended to demonstrate agentic workflow design principles in a compliance automation context. Not for production audit use without domain expert review and expanded control coverage.*
