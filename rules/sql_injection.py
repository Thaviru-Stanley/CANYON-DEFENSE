import ast


def contains_sql_keywords(text):
    sql_keywords = ["select", "insert", "update", "delete"]

    return any(keyword in text.lower() for keyword in sql_keywords)


def get_variable_names(node):
    """
    Recursively collect variable names from AST nodes
    """

    variables = []

    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            variables.append(child.id)

    return variables


def detect(tree, file_path, rule_metadata, tainted_variables):

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):

            sql_found = False

            # Check left side
            if isinstance(node.left, ast.Constant):
                if isinstance(node.left.value, str):
                    if contains_sql_keywords(node.left.value):
                        sql_found = True

            # Check right side
            if isinstance(node.right, ast.Constant):
                if isinstance(node.right.value, str):
                    if contains_sql_keywords(node.right.value):
                        sql_found = True

            if sql_found:

                variables = get_variable_names(node)

                confidence = "MEDIUM"

                for var in variables:
                    if var in tainted_variables:
                        confidence = "HIGH"

                issue = rule_metadata.copy()

                issue.update({
                    "file": file_path,
                    "line": node.lineno,
                    "confidence": confidence
                })

                issues.append(issue)


        if isinstance(node, ast.JoinedStr):

            sql_found = False

            for value in node.values:

                if isinstance(value, ast.Constant):
                    if isinstance(value.value, str):
                        if contains_sql_keywords(value.value):
                            sql_found = True

            if sql_found:

                variables = get_variable_names(node)

                confidence = "MEDIUM"

                for var in variables:
                    if var in tainted_variables:
                        confidence = "HIGH"

                issue = rule_metadata.copy()

                issue.update({
                    "file": file_path,
                    "line": node.lineno,
                    "confidence": confidence
                })

                issues.append(issue)


        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Attribute):

                if node.func.attr == "format":

                    if isinstance(node.func.value, ast.Constant):

                        if isinstance(node.func.value.value, str):

                            if contains_sql_keywords(node.func.value.value):

                                confidence = "MEDIUM"

                                variables = get_variable_names(node)

                                for var in variables:
                                    if var in tainted_variables:
                                        confidence = "HIGH"

                                issue = rule_metadata.copy()

                                issue.update({
                                    "file": file_path,
                                    "line": node.lineno,
                                    "confidence": confidence
                                })

                                issues.append(issue)

    return issues