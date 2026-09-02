import sys
sys.path.insert(0, "src/pycsl")
import ast, json
src = open("src/self-annotate/src/module6_whyml/expressions.py").read()
tree = ast.parse(src)
# find _coerce_to_int
from frontend.Module5_IREmitter import *
import frontend.Module5_IREmitter as M5
# Just locate the function and print its AST dump of the for loop
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_coerce_to_int":
        for st in node.body:
            if isinstance(st, ast.Assign) and isinstance(st.value, ast.Tuple):
                print("ASSIGN-TUPLE targets:", [ast.dump(t) for t in st.targets])
                print("  elts:", [ast.dump(e) for e in st.value.elts][:2])
            if isinstance(st, ast.For):
                print("FOR target:", ast.dump(st.target), "iter:", ast.dump(st.iter))
