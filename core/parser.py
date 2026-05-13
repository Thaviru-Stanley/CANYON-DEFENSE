import ast
def parse_code(code):
    try:
        tree = ast.parse(code)
        return tree
    except SyntaxError as e:
        print(f"Syntax error while parsing code: {e}")
        return None