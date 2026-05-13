from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


def retrieve_controls(query, kb):

    control_texts = []

    for item in kb:
        text = (
            item["Control Name"] + " " +
            item["Description"]
        )

        control_texts.append(text)

    # Generate embeddings
    query_embedding = model.encode([query])

    control_embeddings = model.encode(control_texts)

    # Compute similarity
    similarities = cosine_similarity(
        query_embedding,
        control_embeddings
    )[0]

    # Attach scores
    scored_results = list(zip(similarities, kb))

    # Sort by similarity
    scored_results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # Return top matches
    top_controls = [
        item for score, item in scored_results[:3]
        if score > 0.3
    ]

    return top_controls