def calculate_score(issues):
    """
    Calculates overall security score based on severity and confidence.
    Returns final score out of 100.
    """

    severity_weights = {
        "HIGH": 5,
        "MEDIUM": 3,
        "LOW": 1
    }

    confidence_multiplier = {
        "HIGH": 1.0,
        "MEDIUM": 0.75,
        "LOW": 0.5
    }

    total_risk = 0

    for issue in issues:
        severity = issue.get("severity", "LOW")
        confidence = issue.get("confidence", "HIGH")

        weight = severity_weights.get(severity, 1)
        multiplier = confidence_multiplier.get(confidence, 1.0)

        total_risk += weight * multiplier

    final_score = max(100 - int(total_risk * 5), 0)

    return final_score