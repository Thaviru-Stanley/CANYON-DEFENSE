def generate_html_report(issues, score, output_file="report.html"):
    risk_level = "LOW"
    if score < 60:
        risk_level = "HIGH"
    elif score < 85:
        risk_level = "MODERATE"

    html_content = f"""
    <html>
    <head>
        <title>Canyon Defense Report</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            .summary-box {{ padding: 15px; background-color: #f4f6f7; border-left: 5px solid #2c3e50; margin-bottom: 30px; }}
            .issue-box {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 6px; }}
            .high {{ color: red; }}
            .medium {{ color: orange; }}
            .low {{ color: green; }}
            .label {{ font-weight: bold; }}
            .safe-box {{
                background-color: #d4edda;
                color: #155724;
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
                border: 1px solid #c3e6cb;
            }}
        </style>
    </head>
    <body>

    <h1>Canyon Defense - Security Report</h1>

    <div class="summary-box">
        <h2>Summary</h2>
        <p><strong>Total Issues:</strong> {len(issues)}</p>
        <p><strong>Security Score:</strong> {score}/100</p>
        <p><strong>Risk Level:</strong> {risk_level}</p>
    </div>

    """
    # If no vulnerabilities found
    if not issues:

        html_content += """
        <div class='safe-box'>

            <h3>No vulnerabilities detected</h3>

            <p>
                The scanned project did not contain any detectable security vulnerabilities.
            </p>

        </div>
        """

    # If vulnerabilities exist
    else:

        html_content += "<h2>Detailed Findings</h2>"

        for issue in issues:
            severity_class = issue["severity"].lower()

            html_content += f"""
            <div class="issue-box">
                <p class="{severity_class}"><span class="label">Severity:</span> {issue['severity']}</p>
                <p><span class="label">Confidence:</span> {issue.get('confidence', 'N/A')}</p>
                <p><span class="label">Vulnerability:</span> {issue['name']}</p>
                <p><span class="label">File:</span> {issue['file']}</p>
                <p><span class="label">Line:</span> {issue['line']}</p>
                <p><span class="label">CWE:</span> {issue['cwe']}</p>
                <p><span class="label">OWASP:</span> {issue['owasp']}</p>
                <hr>
                <p><span class="label">Description:</span><br>{issue.get('description', '')}</p>
                <p><span class="label">Impact:</span><br>{issue.get('impact', '')}</p>
                <p><span class="label">Recommended Fix:</span><br>{issue.get('fix', '')}</p>
            </div>
            """

    html_content += """
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nHTML report generated: {output_file}")