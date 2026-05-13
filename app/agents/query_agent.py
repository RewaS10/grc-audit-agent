def extract_keywords(query):
    query = query.lower()
    keywords = []

    if "access" in query:
        keywords.append("access")

    if "data" in query or "encryption" in query:
        keywords.append("data")

    if "log" in query or "monitor" in query:
        keywords.append("log")

    return keywords