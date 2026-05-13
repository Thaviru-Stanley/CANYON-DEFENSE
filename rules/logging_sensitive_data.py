import ast


SENSITIVE_KEYWORDS = [
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "access_key",
    "auth",
    "credential",
    "jwt",
    "session",
    "cookie"
]


LOGGING_FUNCTIONS = [
    "print",
    "info",
    "debug",
    "warning",
    "error",
    "critical",
    "exception"
]


def contains_sensitive_keyword(text):

    text = text.lower()

    return any(
        keyword in text
        for keyword in SENSITIVE_KEYWORDS
    )


def is_logging_call(node):

    # print()
    if isinstance(node.func, ast.Name):

        if node.func.id == "print":
            return True

    # logging.info(), logger.debug(), etc.
    if isinstance(node.func, ast.Attribute):

        if node.func.attr in LOGGING_FUNCTIONS:
            return True

    return False


def contains_sensitive_data(node, tainted_variables):

    for child in ast.walk(node):

        # Variable names
        if isinstance(child, ast.Name):

            if contains_sensitive_keyword(child.id):
                return True

            if child.id in tainted_variables:
                return True

        # String constants
        if isinstance(child, ast.Constant):

            if isinstance(child.value, str):

                if contains_sensitive_keyword(child.value):
                    return True

        # f-string formatted values
        if isinstance(child, ast.FormattedValue):

            if isinstance(child.value, ast.Name):

                if contains_sensitive_keyword(child.value.id):
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

            if is_logging_call(node):

                confidence = "MEDIUM"

                sensitive_found = False

                for arg in node.args:

                    # Direct sensitive variables
                    if isinstance(arg, ast.Name):

                        if contains_sensitive_keyword(arg.id):
                            sensitive_found = True
                            confidence = "HIGH"

                        elif arg.id in tainted_variables:
                            sensitive_found = True
                            confidence = "HIGH"

                    # String concatenation
                    elif isinstance(arg, ast.BinOp):

                        if contains_sensitive_data(arg, tainted_variables):
                            sensitive_found = True
                            confidence = "HIGH"

                    # f-string
                    elif isinstance(arg, ast.JoinedStr):

                        if contains_sensitive_data(arg, tainted_variables):
                            sensitive_found = True
                            confidence = "HIGH"

                    # format()
                    elif isinstance(arg, ast.Call):

                        if contains_sensitive_data(arg, tainted_variables):
                            sensitive_found = True
                            confidence = "HIGH"

                    # Direct string literals
                    elif isinstance(arg, ast.Constant):

                        if isinstance(arg.value, str):

                            if contains_sensitive_keyword(arg.value):
                                sensitive_found = True
                                confidence = "MEDIUM"

                if sensitive_found:

                    issues.append(
                        create_issue(
                            rule_metadata,
                            file_path,
                            node.lineno,
                            confidence
                        )
                    )

    return issues