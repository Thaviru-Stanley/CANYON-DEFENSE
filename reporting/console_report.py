def display_report(issues, score):
    """
    Displays formatted console output for scan results.
    """

    print("\nScan Results")
    print("-" * 50)

    if not issues:
        print("No vulnerabilities detected.")
    else:
        for issue in issues:
            print(f"[{issue['severity']}] {issue['name']}")
            print(f"Confidence: {issue['confidence']}")
            print(f"File: {issue['file']}")
            print(f"Line: {issue['line']}")
            print(f"CWE: {issue['cwe']}")
            print(f"OWASP: {issue['owasp']}")
            print(f"Description: {issue['description']}")
            print(f"Impact: {issue['impact']}")
            print(f"Recommended Fix: {issue['fix']}")
            print("-" * 50)

    print("\nSummary")
    print("-" * 50)
    print(f"Total Issues Found: {len(issues)}")
    print(f"Security Score: {score}/100")

    if score >= 85:
        risk_level = "LOW"
    elif score >= 60:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    print(f"Overall Risk Level: {risk_level}")
    print("=" * 50)