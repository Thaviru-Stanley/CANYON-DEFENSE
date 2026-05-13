import ast


WEAK_HASH_ALGORITHMS = [
    "md5",
    "sha1"
]


WEAK_CIPHERS = [
    "des",
    "rc2",
    "rc4",
    "blowfish"
]


def create_issue(rule_metadata, file_path, line, confidence):

    issue = rule_metadata.copy()

    issue.update({
        "file": file_path,
        "line": line,
        "confidence": confidence
    })

    return issue


def is_weak_hash(node):

    if not isinstance(node.func, ast.Attribute):
        return False

    algorithm = node.func.attr.lower()

    return algorithm in WEAK_HASH_ALGORITHMS


def is_weak_cipher(node):

    if not isinstance(node.func, ast.Attribute):
        return False

    cipher_name = node.func.attr.lower()

    return cipher_name in WEAK_CIPHERS


def contains_sensitive_context(node):

    sensitive_keywords = [
        "password",
        "passwd",
        "pwd",
        "token",
        "secret",
        "auth",
        "credential",
        "hash"
    ]

    for child in ast.walk(node):

        # Variable names
        if isinstance(child, ast.Name):

            if any(
                keyword in child.id.lower()
                for keyword in sensitive_keywords
            ):
                return True

        # String literals
        if isinstance(child, ast.Constant):

            if isinstance(child.value, str):

                if any(
                    keyword in child.value.lower()
                    for keyword in sensitive_keywords
                ):
                    return True

    return False


def detect(tree, file_path, rule_metadata, tainted_variables):

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            confidence = None

            if is_weak_hash(node):

                confidence = "MEDIUM"

                if contains_sensitive_context(node):
                    confidence = "HIGH"


            elif is_weak_cipher(node):

                confidence = "HIGH"

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