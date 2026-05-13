"""
retrieval_agent.py
──────────────────────────────────────────────────────────────
Semantic Retrieval Agent

Responsibilities:
- Loads SentenceTransformer embedding model (all-MiniLM-L6-v2)
- Converts control descriptions into dense vector embeddings
- Embeds the enriched user query
- Computes cosine similarity across all control vectors
- Returns top-N controls ranked by semantic relevance score

This replaces keyword-based matching with meaning-aware retrieval:
a query about "customer data safety" correctly matches
"Data Encryption" without any shared keywords.
──────────────────────────────────────────────────────────────
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
from agents.query_agent import ProcessedQuery

# ── Model (loaded once at import time) ───────────────────────

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


# ── Embedding helpers ─────────────────────────────────────────

def _embed(texts: list[str]) -> np.ndarray:
    model = _get_model()
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def _build_control_text(record: dict) -> str:
    """
    Concatenate control fields into a single string for embedding.
    Weighting title + description most heavily.
    """
    parts = []
    for field in ["Control Name", "Description", "Evidence Required"]:
        val = record.get(field, "")
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    return " ".join(parts)


# ── Main retrieval function ───────────────────────────────────

def retrieve_controls(
    processed_query: ProcessedQuery,
    knowledge_base: list[dict],
    top_k: int = 5,
    min_score: float = 0.25
) -> list[dict]:
    """
    Semantically retrieve the top-K most relevant controls
    from the knowledge base for the given processed query.

    Parameters
    ----------
    processed_query : ProcessedQuery
        Output from query_agent.process_query()
    knowledge_base  : list[dict]
        List of control records (from pandas DataFrame.to_dict())
    top_k           : int
        Maximum number of controls to return
    min_score       : float
        Minimum cosine similarity threshold (0–1)

    Returns
    -------
    list[dict]
        Control records enriched with a `similarity_score` field,
        sorted descending by score.
    """
    if not knowledge_base:
        return []

    # Build control text corpus
    control_texts = [_build_control_text(rec) for rec in knowledge_base]

    # Embed query and controls
    query_vec    = _embed([processed_query.enriched])          # (1, D)
    control_vecs = _embed(control_texts)                       # (N, D)

    # Cosine similarity
    scores = cosine_similarity(query_vec, control_vecs)[0]     # (N,)

    # Rank and filter
    ranked_indices = np.argsort(scores)[::-1]

    results = []
    for idx in ranked_indices[:top_k]:
        score = float(scores[idx])
        if score < min_score:
            break
        record = dict(knowledge_base[idx])
        record["similarity_score"] = round(score, 4)
        results.append(record)

    return results


# ── Convenience wrapper for direct string input ───────────────

def retrieve_controls_from_query(
    raw_query: str,
    knowledge_base: list[dict],
    top_k: int = 5,
    min_score: float = 0.25
) -> list[dict]:
    """
    Convenience function: accepts a raw string, runs it through
    the query agent, then performs retrieval.
    """
    from agents.query_agent import process_query
    pq = process_query(raw_query)
    return retrieve_controls(pq, knowledge_base, top_k, min_score)


# ── CLI test ──────────────────────────────────────────────────

if __name__ == "__main__":
    import pandas as pd, os

    csv_path = os.path.join(
        os.path.dirname(__file__), "../../data/SOC2_tracker - Sheet1.csv"
    )
    df = pd.read_csv(csv_path)
    kb = df.to_dict(orient="records")

    test_queries = [
        "How is sensitive data protected at rest and in transit?",
        "Who can access production systems and how is that controlled?",
        "What monitoring is in place for detecting security incidents?"
    ]

    for q in test_queries:
        print(f"\n{'─'*60}")
        print(f"Query : {q}")
        results = retrieve_controls_from_query(q, kb, top_k=3)
        for r in results:
            print(f"  [{r.get('Control ID','?')}] {r.get('Control Name','?')} — score: {r['similarity_score']}")