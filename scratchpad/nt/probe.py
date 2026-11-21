import sys, ast, json
sys.path.insert(0, "src/pycsl")
src = open("src/self-annotate/src/module6_whyml/expressions.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_namedtuple_positional_access":
        for s in ast.walk(node):
            if isinstance(s, ast.For):
                print("FOR target:", ast.dump(s.target))
                print("FOR iter:", ast.dump(s.iter))
