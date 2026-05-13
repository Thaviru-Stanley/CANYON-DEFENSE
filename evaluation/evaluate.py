import os
from core.file_loader import load_files
from core.parser import parse_code
from core.scanner import scan_tree


def scan_folder(folder_path):
    all_issues = []

    files = load_files(folder_path)

    for file_path, code in files:
        tree = parse_code(code)
        issues = scan_tree(tree, file_path)
        all_issues.extend(issues)

    return all_issues


def evaluate():
    vulnerable_path = "evaluation/vulnerable"
    secure_path = "evaluation/secure"

    vulnerable_issues = scan_folder(vulnerable_path)
    secure_issues = scan_folder(secure_path)

    TP = len(vulnerable_issues)
    FP = len(secure_issues)

    # We intentionally placed 7 vulnerabilities
    EXPECTED_VULNERABILITIES = 7

    FN = EXPECTED_VULNERABILITIES - TP
    if FN < 0:
        FN = 0

    # Metrics
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    print("\nEvaluation Results")
    print("-" * 40)
    print(f"True Positives (TP): {TP}")
    print(f"False Positives (FP): {FP}")
    print(f"False Negatives (FN): {FN}")
    print("-" * 40)
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print("=" * 40)


if __name__ == "__main__":
    evaluate()