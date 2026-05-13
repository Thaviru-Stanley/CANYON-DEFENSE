import ast


DEBUG_FUNCTIONS = [
    "run"
]


DEBUG_KEYWORDS = [
    "debug"
]


def create_issue(rule_metadata, file_path, line, confidence):

    issue = rule_metadata.copy()

    issue.update({
        "file": file_path,
        "line": line,
        "confidence": confidence
    })

    return issue


def contains_debug_keywords(node):

    debug_terms = [
        "debug",
        "traceback",
        "stacktrace",
        "exception"
    ]

    for child in ast.walk(node):

        # Variable names
        if isinstance(child, ast.Name):

            if any(term in child.id.lower() for term in debug_terms):
                return True

        # String literals
        if isinstance(child, ast.Constant):

            if isinstance(child.value, str):

                if any(term in child.value.lower() for term in debug_terms):
                    return True

    return False


def detect(tree, file_path, rule_metadata, tainted_variables):

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            confidence = None

            if isinstance(node.func, ast.Attribute):

                if node.func.attr in DEBUG_FUNCTIONS:

                    for keyword in node.keywords:

                        # debug=True
                        if keyword.arg in DEBUG_KEYWORDS:

                            # app.run(debug=True)
                            if isinstance(keyword.value, ast.Constant):

                                if keyword.value.value is True:
                                    confidence = "HIGH"

                            # app.run(debug=debug_mode)
                            elif isinstance(keyword.value, ast.Name):

                                confidence = "MEDIUM"


            elif isinstance(node.func, ast.Name):

                if node.func.id in [
                    "print",
                    "traceback",
                    "format_exc"
                ]:

                    if contains_debug_keywords(node):
                        confidence = "MEDIUM"


            if isinstance(node.func, ast.Attribute):

                if node.func.attr in [
                    "exception",
                    "error",
                    "critical"
                ]:

                    if contains_debug_keywords(node):
                        confidence = "MEDIUM"


            if confidence:

                issues.append(
                    create_issue(
                        rule_metadata,
                        file_path,
                        node.lineno,
                        confidence
                    )
                )

    return issues