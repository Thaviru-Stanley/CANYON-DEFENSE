import ast

def get_tainted_variables(tree):
    """
    Tracks variables assigned from user input sources.
    Returns a set of tainted variable names.
    """

    tainted = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            # Example: user_input = input()
            if isinstance(node.value, ast.Call):

                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id == "input":

                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                tainted.add(target.id)

    return tainted