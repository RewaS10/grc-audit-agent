import pandas as pd

from agents.query_agent import extract_keywords
from agents.retrieval_agent import retrieve_controls
from agents.analysis_agent import generate_response




# Load CSV
df = pd.read_csv("../data/SOC2_tracker - Sheet1.csv")

# Convert to knowledge base
knowledge_base = df.to_dict(orient="records")


# User input
query = input("Enter your audit query: ")


# Agent Workflow
controls = retrieve_controls(
    query,
    knowledge_base
)

response = generate_response(
    query,
    controls
)


print("\n=== AI AUDIT RESPONSE ===\n")

print(response)