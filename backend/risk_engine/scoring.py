severity_scores = {
    "LOW": 2,
    "MEDIUM": 5,
    "HIGH": 8,
    "CRITICAL": 10
}


def calculate_risk_score(findings):
    total = 0
    breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    for finding in findings:
        severity = finding.get("severity", "LOW")
        total += severity_scores.get(severity, 0)
        if severity in breakdown:
            breakdown[severity] += 1

    return total


def calculate_risk_summary(findings):
    """Return a structured risk summary with breakdown by severity."""
    total = 0
    breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    for finding in findings:
        severity = finding.get("severity", "LOW")
        total += severity_scores.get(severity, 0)
        if severity in breakdown:
            breakdown[severity] += 1

    return {
        "total_score": total,
        "risk_count": len(findings),
        "breakdown": breakdown
    }