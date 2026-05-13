def generate_response(query, controls):

    if not controls:
        return {
            "message": "No relevant controls found."
        }

    risks = []
    recommendations = []
    compliance = []

    for c in controls:

        description = c["Description"]

        if "encrypt" in description.lower():
            risks.append("Potential data breach risk")
            recommendations.append(
                "Ensure encryption is enabled for sensitive data."
            )

        if "access" in description.lower():
            risks.append("Unauthorized access risk")
            recommendations.append(
                "Review role-based access controls regularly."
            )

        compliance.append(c["Control ID"])

    return {
        "query": query,
        "matched_controls": [
            c["Control Name"] for c in controls
        ],
        "risk_analysis": list(set(risks)),
        "recommendations": list(set(recommendations)),
        "compliance_mapping": list(set(compliance))
    }