"""
main.py
──────────────────────────────────────────────────────────────
GRC Intelligence Engine — CLI Entry Point

Usage:
    python main.py
    python main.py --query "How is sensitive data protected?"
    python main.py --query "..." --top-k 3 --min-score 0.30
──────────────────────────────────────────────────────────────
"""

import os
import sys
import argparse
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# PATH CONFIGURATION
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "../data/SOC2_tracker - Sheet1.csv"
)

# Allow package imports
sys.path.insert(0, BASE_DIR)

# ─────────────────────────────────────────────
# AGENT IMPORTS
# ─────────────────────────────────────────────

from agents.query_agent import process_query
from agents.retrieval_agent import retrieve_controls
from agents.analysis_agent import generate_response


# ─────────────────────────────────────────────
# LOAD KNOWLEDGE BASE
# ─────────────────────────────────────────────

def load_knowledge_base(path: str) -> list[dict]:

    if not os.path.exists(path):

        print(f"\n[ERROR] Knowledge base not found:\n{path}")
        print("\nPlace the CSV inside the /data directory.\n")

        sys.exit(1)

    df = pd.read_csv(path)

    print(f"\n[✓] Knowledge base loaded — {len(df)} controls indexed")

    return df.to_dict(orient="records")


# ─────────────────────────────────────────────
# REPORT PRINTER
# ─────────────────────────────────────────────

def print_report(report) -> None:

    divider = "─" * 70

    print(f"\n{divider}")
    print(f"  GRC AUDIT REPORT  ·  {report.report_id}")
    print(f"  {report.timestamp}")
    print(divider)

    print(f"\n  QUERY")
    print(f"  {report.query}")

    if report.intent:
        print(f"\n  DETECTED INTENT")
        print(f"  {report.intent}")

    print(f"\n  OVERALL RISK LEVEL")
    print(f"  {report.risk_level}")

    # ─────────────────────
    # CONTROLS
    # ─────────────────────

    print(f"\n  MATCHED CONTROLS ({len(report.matched_controls)})")

    if report.matched_controls:

        for idx, (control, score) in enumerate(
            zip(report.matched_controls, report.similarity_scores),
            start=1
        ):

            print(
                f"    {idx}. {control}"
                f"  [similarity: {score:.3f}]"
            )

    else:
        print("    No controls matched.")

    # ─────────────────────
    # RISKS
    # ─────────────────────

    print(f"\n  RISK ANALYSIS")

    for risk in report.risk_analysis:
        print(f"    ▲ {risk}")

    # ─────────────────────
    # RECOMMENDATIONS
    # ─────────────────────

    print(f"\n  RECOMMENDATIONS")

    for rec in report.recommendations:
        print(f"    → {rec}")

    # ─────────────────────
    # FRAMEWORKS
    # ─────────────────────

    print(f"\n  COMPLIANCE FRAMEWORKS")

    for framework in report.compliance_mapping:
        print(f"    ✓ {framework}")

    # ─────────────────────
    # EVIDENCE
    # ─────────────────────

    if report.evidence_required:

        print(f"\n  EVIDENCE REQUIRED")

        for ev in report.evidence_required:
            print(f"    · {ev}")

    # ─────────────────────
    # OWNERS
    # ─────────────────────

    if report.control_owners:

        print(f"\n  CONTROL OWNERS")

        for owner in sorted(set(report.control_owners)):
            print(f"    · {owner}")

    # ─────────────────────
    # STATUS
    # ─────────────────────

    if report.control_statuses:

        print(f"\n  CONTROL STATUS")

        for status in report.control_statuses:
            print(f"    · {status}")

    print(f"\n{divider}\n")


# ─────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────

def main():

    parser = argparse.ArgumentParser(
        description="GRC Intelligence Engine — CLI Audit Assistant"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=None,
        help="Audit query string"
    )

    parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=5,
        help="Maximum number of controls to retrieve"
    )

    parser.add_argument(
        "--min-score",
        "-s",
        type=float,
        default=0.25,
        help="Minimum cosine similarity threshold"
    )

    args = parser.parse_args()

    # ─────────────────────
    # HEADER
    # ─────────────────────

    print("\n🛡️  GRC Intelligence Engine")
    print("Semantic Retrieval · Agentic Workflow · Compliance Intelligence\n")

    # ─────────────────────
    # LOAD KB
    # ─────────────────────

    knowledge_base = load_knowledge_base(DATA_PATH)

    # ─────────────────────
    # QUERY INPUT
    # ─────────────────────

    query = args.query

    if not query:

        query = input("Enter audit query: ").strip()

        if not query:

            print("\n[ERROR] No query provided.\n")

            sys.exit(1)

    # ─────────────────────
    # QUERY AGENT
    # ─────────────────────

    print("\n[→] Processing query...")

    processed_query = process_query(query)

    print(
        f"[→] Intent detected: "
        f"{processed_query.intent or 'general'} "
        f"({processed_query.confidence})"
    )

    # ─────────────────────
    # RETRIEVAL AGENT
    # ─────────────────────

    print(
        f"[→] Running semantic retrieval "
        f"(top-{args.top_k}, threshold={args.min_score})..."
    )

    controls = retrieve_controls(
        processed_query,
        knowledge_base,
        top_k=args.top_k,
        min_score=args.min_score
    )

    print(f"[✓] {len(controls)} controls matched")

    # ─────────────────────
    # ANALYSIS AGENT
    # ─────────────────────

    print("[→] Generating audit report...")

    report = generate_response(
        processed_query,
        controls
    )

    # ─────────────────────
    # OUTPUT REPORT
    # ─────────────────────

    print_report(report)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()