from core.file_loader import load_files
from core.parser import parse_code
from core.scanner import scan_tree
from reporting.console_report import display_report
from scoring.risk_score import calculate_score
from reporting.html_report import generate_html_report

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

import os
import webbrowser


# CustomTKinter Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


BG_COLOR = "#14161a"
CARD_COLOR = "#1d1f23"
RED = "#ff003c"
HOVER_RED = "#cc0030"
TEXT = "#f5f5f5"
GRAY = "#b0b0b0"


# Global Variable
selected_files_data = []
selected_directory = None


# File Selection
def select_files():

    global selected_files_data
    global selected_directory

    selected_directory = None
    selected_files_data = []

    file_paths = filedialog.askopenfilenames(
        title="Select Python Files",
        filetypes=[("Python Files", "*.py")]
    )

    if not file_paths:
        return

    for file_path in file_paths:

        try:
            with open(file_path, "r", encoding="utf-8") as f:

                code = f.read()

                selected_files_data.append((file_path, code))

        except Exception as e:

            messagebox.showerror(
                "File Error",
                f"Error reading file:\n{e}"
            )

    status_label.configure(
        text=f"{len(selected_files_data)} Python file(s) selected"
    )


# Directory Selection
def select_directory():

    global selected_directory
    global selected_files_data

    selected_files_data = []

    directory = filedialog.askdirectory(
        title="Select Project Directory"
    )

    if not directory:
        return

    selected_directory = directory

    status_label.configure(
        text=f"Directory Selected:\n{selected_directory}"
    )


# Show Results page
def show_results_page(results_text):

    home_page.pack_forget()

    results_page.pack(fill="both", expand=True)

    results_box.delete("1.0", "end")

    results_box.insert("end", results_text)


# Back to Home page
def return_home():

    global selected_files_data
    global selected_directory

    # Clear Previous Selections
    selected_files_data = []

    selected_directory = None

    # Reset Status Label
    status_label.configure(
        text="No files or directories selected"
    )

    # Switch Pages
    results_page.pack_forget()

    home_page.pack(fill="both", expand=True)


# Open HTML report
def open_report():

    report_path = os.path.abspath("report.html")

    webbrowser.open(f"file://{report_path}")


# Start Scan
def start_scan():

    files = []

    # File mode
    if selected_files_data:

        files = selected_files_data

    # Directory mode
    elif selected_directory:

        files = load_files(selected_directory)

    else:

        messagebox.showwarning(
            "No Selection",
            "Please select Python files or a directory."
        )

        return

    if not files:

        messagebox.showwarning(
            "No Python Files",
            "No Python files were found."
        )

        return

    all_issues = []

    # Scan files
    for file_path, code in files:

        tree = parse_code(code)

        if tree is None:
            continue

        issues = scan_tree(tree, file_path)

        all_issues.extend(issues)

    # Calculatate Score
    score = calculate_score(all_issues)

    # Reports
    display_report(all_issues, score)

    generate_html_report(all_issues, score)

    # Build results text
    results_text = ""

    results_text += "CANYON DEFENSE — SCAN RESULTS\n"
    results_text += "=" * 60 + "\n\n"

    results_text += f"Total Vulnerabilities Found: {len(all_issues)}\n"

    results_text += f"Risk Score: {score}\n\n"

    if not all_issues:

        results_text += "No vulnerabilities detected.\n"

    else:

        for issue in all_issues:

            results_text += (
                f"[ {issue['severity']} ] "
                f"{issue['name']}\n"
            )

            results_text += (
                f"File: {issue['file']}\n"
            )

            if 'line' in issue:

                results_text += (
                    f"Line: {issue['line']}\n"
                )

            results_text += "-" * 60 + "\n"

    # Show results page
    show_results_page(results_text)


# Main window
root = ctk.CTk()

root.title("CANYON DEFENSE")


# Auto screen fit
screen_width = root.winfo_screenwidth()

screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.92)

window_height = int(screen_height * 0.90)

x_position = int((screen_width - window_width) / 2)

y_position = int((screen_height - window_height) / 2)

root.geometry(
    f"{window_width}x{window_height}+{x_position}+{y_position}"
)

root.minsize(1200, 700)

root.configure(fg_color=BG_COLOR)


# Main container
container = ctk.CTkFrame(
    root,
    fg_color=BG_COLOR,
    corner_radius=0
)

container.pack(fill="both", expand=True)


# Home page
home_page = ctk.CTkFrame(
    container,
    fg_color=BG_COLOR,
    corner_radius=0
)

home_page.pack(fill="both", expand=True)


# Sidebar
sidebar = ctk.CTkFrame(
    home_page,
    width=280,
    fg_color="#111317",
    corner_radius=0
)

sidebar.pack(side="left", fill="y")

sidebar.pack_propagate(False)


# Logo
logo_image = ctk.CTkImage(
    light_image=Image.open("logo.webp"),
    dark_image=Image.open("logo.webp"),
    size=(170, 170)
)

logo_label = ctk.CTkLabel(
    sidebar,
    image=logo_image,
    text=""
)

logo_label.pack(pady=(25, 10))


# Title
name_label = ctk.CTkLabel(
    sidebar,
    text="CANYON\nDEFENSE",
    text_color=RED,
    font=("Arial", 30, "bold")
)

name_label.pack()


subtitle = ctk.CTkLabel(
    sidebar,
    text="Python Vulnerability Scanner",
    text_color=GRAY,
    font=("Arial", 13)
)

subtitle.pack(pady=(5, 15))


vuln_title = ctk.CTkLabel(
    sidebar,
    text="OWASP VULNERABILITIES",
    text_color=RED,
    font=("Arial", 16, "bold")
)

vuln_title.pack(pady=(10, 10))


vulnerabilities = [
    "• Hardcoded Secrets",
    "• SQL Injection",
    "• Weak Cryptography",
    "• Logging Sensitive Data",
    "• Command Injection",
    "• Insecure Deserialization",
    "• Insecure Error Handling"
]


for vuln in vulnerabilities:

    vuln_label = ctk.CTkLabel(
        sidebar,
        text=vuln,
        text_color="#d6d6d6",
        anchor="w",
        justify="left",
        font=("Arial", 13)
    )

    vuln_label.pack(
        anchor="w",
        padx=35,
        pady=6
    )


# Main content
main_frame = ctk.CTkFrame(
    home_page,
    fg_color=BG_COLOR,
    corner_radius=0
)

main_frame.pack(fill="both", expand=True)


# Content Box
content_box = ctk.CTkFrame(
    main_frame,
    fg_color="#181a1f",
    border_color="#2d2f34",
    border_width=1,
    corner_radius=18
)

content_box.pack(
    padx=40,
    pady=25,
    fill="both",
    expand=True
)


# Header
header = ctk.CTkLabel(
    content_box,
    text="WELCOME TO CANYON DEFENSE",
    text_color=RED,
    font=("Arial", 40, "bold")
)

header.pack(pady=(20, 10))


subheader = ctk.CTkLabel(
    content_box,
    text=(
        "Static Application Security "
        "Testing for Python Applications"
    ),
    text_color=TEXT,
    font=("Arial", 15)
)

subheader.pack()


# Card Frame
card_frame = ctk.CTkFrame(
    content_box,
    fg_color="transparent"
)

card_frame.pack(pady=50)


# File card
file_card = ctk.CTkFrame(
    card_frame,
    width=350,
    height=250,
    fg_color=CARD_COLOR,
    border_color=RED,
    border_width=1,
    corner_radius=20
)
file_card.grid(row=0, column=0, padx=25)
file_card.pack_propagate(False)


file_title = ctk.CTkLabel(
    file_card,
    text="SCAN FILES",
    text_color=RED,
    font=("Arial", 24, "bold")
)
file_title.pack(pady=(35, 15))


file_desc = ctk.CTkLabel(
    file_card,
    text="Select one or more Python files for vulnerability analysis.",
    text_color=TEXT,
    font=("Arial", 12)
)
file_desc.pack(pady=(0, 25))


file_button = ctk.CTkButton(
    file_card,
    text="SELECT FILES",
    command=select_files,
    fg_color=RED,
    hover_color=HOVER_RED,
    text_color="white",
    corner_radius=12,
    width=200,
    height=45,
    font=("Arial", 13, "bold")
)
file_button.pack()


# Directory card
directory_card = ctk.CTkFrame(
    card_frame,
    width=350,
    height=250,
    fg_color=CARD_COLOR,
    border_color=RED,
    border_width=1,
    corner_radius=20
)

directory_card.grid(row=0, column=1, padx=25)
directory_card.pack_propagate(False)


folder_title = ctk.CTkLabel(
    directory_card,
    text="SCAN DIRECTORY",
    text_color=RED,
    font=("Arial", 24, "bold")
)
folder_title.pack(pady=(35, 15))


folder_desc = ctk.CTkLabel(
    directory_card,
    text="Recursively scan an entire Python project directory.",
    text_color=TEXT,
    font=("Arial", 12)
)
folder_desc.pack(pady=(0, 25))


folder_button = ctk.CTkButton(
    directory_card,
    text="SELECT DIRECTORY",
    command=select_directory,
    fg_color=RED,
    hover_color=HOVER_RED,
    text_color="white",
    corner_radius=12,
    width=220,
    height=45,
    font=("Arial", 13, "bold")
)
folder_button.pack()


# Status
status_label = ctk.CTkLabel(
    content_box,
    text="No files or directories selected",
    text_color=GRAY,
    font=("Arial", 13)
)

status_label.pack(pady=15)


# Start scan
scan_button = ctk.CTkButton(
    content_box,
    text="START SECURITY SCAN",
    command=start_scan,
    fg_color=RED,
    hover_color=HOVER_RED,
    border_width=1,
    border_color="#ff335f",
    corner_radius=16,
    width=320,
    height=55,
    font=("Arial", 16, "bold")
)

scan_button.pack(pady=20)


# Results page
results_page = ctk.CTkFrame(
    container,
    fg_color=BG_COLOR,
    corner_radius=0
)


results_title = ctk.CTkLabel(
    results_page,
    text="SCAN RESULTS",
    text_color=RED,
    font=("Arial", 38, "bold")
)

results_title.pack(pady=(40, 20))


results_box = ctk.CTkTextbox(
    results_page,
    width=950,
    height=420,
    fg_color="#1b1d22",
    border_color=RED,
    border_width=1,
    corner_radius=15,
    text_color="white",
    font=("Consolas", 13)
)

results_box.pack(pady=(20,10))


# Results button
results_button_frame = ctk.CTkFrame(
    results_page,
    fg_color="transparent"
)

results_button_frame.pack(pady=20)


view_report_button = ctk.CTkButton(
    results_button_frame,
    text="VIEW HTML REPORT",
    command=open_report,
    fg_color=RED,
    hover_color=HOVER_RED,
    width=220,
    height=50,
    corner_radius=14,
    font=("Arial", 14, "bold")
)

view_report_button.grid(row=0, column=0, padx=15)


scan_again_button = ctk.CTkButton(
    results_button_frame,
    text="SCAN AGAIN",
    command=return_home,
    fg_color="#2d3138",
    hover_color="#40444b",
    width=220,
    height=50,
    corner_radius=14,
    font=("Arial", 14, "bold")
)

scan_again_button.grid(row=0, column=1, padx=15)


root.mainloop()