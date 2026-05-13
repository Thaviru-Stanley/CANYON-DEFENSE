import ast


DANGEROUS_FUNCTIONS = [
    "system",
    "popen",
    "run",
    "call",
    "check_output",
    "check_call"
]


def is_dangerous_call(node):

    if isinstance(node.func, ast.Attribute):

        if node.func.attr in DANGEROUS_FUNCTIONS:
            return True

    return False


def contains_tainted_data(node, tainted_variables):

    for child in ast.walk(node):

        # Variable usage
        if isinstance(child, ast.Name):

            if child.id in tainted_variables:
                return True

        # f-string formatted values
        if isinstance(child, ast.FormattedValue):

            if isinstance(child.value, ast.Name):

                if child.value.id in tainted_variables:
                    return True

    return False


def create_issue(rule_metadata, file_path, line, confidence):

    issue = rule_metadata.copy()

    issue.update({
        "file": file_path,
        "line": line,
        "confidence": confidence
    })

    return issue


def detect(tree, file_path, rule_metadata, tainted_variables):

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if is_dangerous_call(node):

                confidence = "MEDIUM"

                for arg in node.args:

                    # Direct tainted variable
                    if isinstance(arg, ast.Name):

                        if arg.id in tainted_variables:
                            confidence = "HIGH"

                    # String concatenation
                    elif isinstance(arg, ast.BinOp):

                        if contains_tainted_data(arg, tainted_variables):
                            confidence = "HIGH"

                    # f-string
                    elif isinstance(arg, ast.JoinedStr):

                        if contains_tainted_data(arg, tainted_variables):
                            confidence = "HIGH"

                    # format()
                    elif isinstance(arg, ast.Call):

                        if contains_tainted_data(arg, tainted_variables):
                            confidence = "HIGH"

                    # Literal dangerous commands
                    elif isinstance(arg, ast.Constant):

                        if isinstance(arg.value, str):

                            dangerous_keywords = [
                                "rm ",
                                "del ",
                                "shutdown",
                                "curl ",
                                "wget ",
                                "bash ",
                                "powershell",
                                "cmd.exe"
                            ]

                            if any(
                                keyword in arg.value.lower()
                                for keyword in dangerous_keywords
                            ):
                                confidence = "HIGH"


                issues.append(
                    create_issue(
                        rule_metadata,
                        file_path,
                        node.lineno,
                        confidence
                    )
                )

    return issues