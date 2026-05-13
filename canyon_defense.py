from core.file_loader import load_files
from core.parser import parse_code
from core.scanner import scan_tree
from reporting.console_report import display_report
from scoring.risk_score import calculate_score
from reporting.html_report import generate_html_report

import webbrowser
import os
import tkinter as tk
from tkinter import filedialog


def main():
    print("=" * 50)
    print("CANYON DEFENSE - Static Security Analyzer")
    print("=" * 50)

    # Hide tkinter root window
    root = tk.Tk()
    root.withdraw()

    print("\nSelect Python files OR a project directory.")

    # Allow multiple file selection
    selected_files = filedialog.askopenfilenames(
        title="Select Python Files",
        filetypes=[("Python Files", "*.py")]
    )

    files = []

    # If multiple files selected
    if selected_files:
        for file_path in selected_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    files.append((file_path, code))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    else:
        # If no files selected, allow directory selection
        selected_directory = filedialog.askdirectory(
            title="Select Project Directory"
        )

        if not selected_directory:
            print("No file or directory selected!")
            return

        print(f"\nScanning Directory: {selected_directory}")

        files = load_files(selected_directory)

    if not files:
        print("No Python files found!")
        return

    all_issues = []

    # Scan files
    for file_path, code in files:
        tree = parse_code(code)

        if tree is None:
            continue

        issues = scan_tree(tree, file_path)
        all_issues.extend(issues)

    # Calculate score
    score = calculate_score(all_issues)

    # Console report
    display_report(all_issues, score)

    # HTML report
    generate_html_report(all_issues, score)

    # Open HTML report
    user_input = input(
        "\nDo you want to open the HTML report? (yes/no): "
    ).strip().lower()

    if user_input in ["yes", "y"]:
        report_path = os.path.abspath("report.html")
        webbrowser.open(f"file://{report_path}")
        print("Opening report in browser...")
    else:
        print("Report not opened.")


if __name__ == "__main__":
    main()