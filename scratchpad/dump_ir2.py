import ast
src = open("src/self-annotate/src/module6_whyml/expressions.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_coerce_to_int":
        print("FOUND", node.name)
        for st in node.body:
            if isinstance(st, ast.Assign) and isinstance(st.value, ast.Tuple):
                print("ASSIGN-TUPLE targets:", [ast.dump(t) for t in st.targets])
            if isinstance(st, ast.For):
                print("FOR target:", ast.dump(st.target))
                print("     iter:", ast.dump(st.iter))
