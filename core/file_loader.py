import os


def load_files(target_path):
    """
    Loads Python files from a single file or directory.
    Returns a list of (file_path, file_content).
    """

    files_to_scan = []

    if os.path.isfile(target_path):
        if target_path.endswith(".py"):
            with open(target_path, "r", encoding="utf-8") as f:
                files_to_scan.append((target_path, f.read()))

    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="utf-8") as f:
                        files_to_scan.append((full_path, f.read()))

    else:
        print(f"Invalid path: {target_path}")

    return files_to_scan