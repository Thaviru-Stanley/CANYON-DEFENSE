import ast


DANGEROUS_DESERIALIZERS = {
    "pickle": ["load", "loads"],
    "yaml": ["load"],
    "marshal": ["load", "loads"],
    "shelve": ["open"],
    "dill": ["load", "loads"]
}


def is_dangerous_deserialization(node):

    if not isinstance(node.func, ast.Attribute):
        return False

    method_name = node.func.attr

    if isinstance(node.func.value, ast.Name):

        module_name = node.func.value.id

        if module_name in DANGEROUS_DESERIALIZERS:

            if method_name in DANGEROUS_DESERIALIZERS[module_name]:
                return True

    return False


def contains_tainted_data(node, tainted_variables):

    for child in ast.walk(node):

        # user_input
        if isinstance(child, ast.Name):

            if child.id in tainted_variables:
                return True

        # f-string variables
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

            if is_dangerous_deserialization(node):

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


                issues.append(
                    create_issue(
                        rule_metadata,
                        file_path,
                        node.lineno,
                        confidence
                    )
                )

    return issues