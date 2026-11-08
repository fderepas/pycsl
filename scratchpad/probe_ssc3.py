import sys, ast
sys.path.insert(0, "src/pycsl")
from frontend.Module5_IREmitter import PyCSLToJSONEmitter
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
cnt=0
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "IRScanner":
        cnt+=1
        em = PyCSLToJSONEmitter.__new__(PyCSLToJSONEmitter)
        r = em._collect_class_str_set_constants(node, set())
        print("IRScanner found, body len", len(node.body), "-> ", r)
print("count IRScanner top-level:", cnt)
