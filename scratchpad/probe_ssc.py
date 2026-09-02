import sys, ast
sys.path.insert(0, "src/pycsl")
from frontend.Module5_IREmitter import PyCSLToJSONEmitter
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "IRScanner":
        em = PyCSLToJSONEmitter.__new__(PyCSLToJSONEmitter)
        r = em._collect_class_str_set_constants(node, set())
        print("str_set_constants:", r)
