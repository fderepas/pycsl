import sys, ast
sys.path.insert(0, "src/pycsl")
import frontend.Module5_IREmitter as M5
print("ast is same module:", M5.ast is ast)
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
node = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=="IRScanner"][0]
# check the AnnAssign child is recognized by M5.ast
for child in node.body:
    if isinstance(child, M5.ast.AnnAssign) and isinstance(child.target, M5.ast.Name) and "MUTAT" in child.target.id:
        print("M5.ast sees AnnAssign, value is M5.ast.Set?", isinstance(child.value, M5.ast.Set))
em = M5.PyCSLToJSONEmitter.__new__(M5.PyCSLToJSONEmitter)
r = em._collect_class_str_set_constants(node, set())
print("result:", r)
