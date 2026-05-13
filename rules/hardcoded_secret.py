import ast
import re


def is_secret_variable(variable_name):

    secret_keywords = [
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
        "session"
    ]

    variable_name = variable_name.lower()

    return any(keyword in variable_name for keyword in secret_keywords)


def looks_like_secret(value):

    # Ignore very short strings
    if len(value) < 6:
        return False

    # Common hardcoded patterns
    patterns = [
        r"^[A-Za-z0-9_\-]{8,}$",
        r"^sk_[A-Za-z0-9]+",
        r"^AIza[0-9A-Za-z\-_]+",
        r"^[A-Fa-f0-9]{32,}$"
    ]

    for pattern in patterns:
        if re.match(pattern, value):
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

        if isinstance(node, ast.Assign):

            if isinstance(node.value, ast.Constant):

                if isinstance(node.value.value, str):

                    secret_value = node.value.value

                    for target in node.targets:

                        if isinstance(target, ast.Name):

                            variable_name = target.id

                            if is_secret_variable(variable_name):

                                confidence = "HIGH"

                                issues.append(
                                    create_issue(
                                        rule_metadata,
                                        file_path,
                                        node.lineno,
                                        confidence
                                    )
                                )

                            elif looks_like_secret(secret_value):

                                confidence = "MEDIUM"

                                issues.append(
                                    create_issue(
                                        rule_metadata,
                                        file_path,
                                        node.lineno,
                                        confidence
                                    )
                                )


        if isinstance(node, ast.Dict):

            for key, value in zip(node.keys, node.values):

                if isinstance(key, ast.Constant):

                    if isinstance(key.value, str):

                        key_name = key.value.lower()

                        if is_secret_variable(key_name):

                            if isinstance(value, ast.Constant):

                                if isinstance(value.value, str):

                                    issues.append(
                                        create_issue(
                                            rule_metadata,
                                            file_path,
                                            node.lineno,
                                            "HIGH"
                                        )
                                    )


        if isinstance(node, ast.Call):

            for keyword in node.keywords:

                if keyword.arg:

                    if is_secret_variable(keyword.arg):

                        if isinstance(keyword.value, ast.Constant):

                            if isinstance(keyword.value.value, str):

                                issues.append(
                                    create_issue(
                                        rule_metadata,
                                        file_path,
                                        node.lineno,
                                        "HIGH"
                                    )
                                )


        if isinstance(node, ast.JoinedStr):

            for value in node.values:

                if isinstance(value, ast.Constant):

                    if isinstance(value.value, str):

                        text = value.value.lower()

                        if any(keyword in text for keyword in [
                            "password",
                            "secret",
                            "token",
                            "api_key",
                            "apikey"
                        ]):

                            issues.append(
                                create_issue(
                                    rule_metadata,
                                    file_path,
                                    node.lineno,
                                    "MEDIUM"
                                )
                            )

    return issues