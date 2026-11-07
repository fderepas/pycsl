import sys, ast, importlib.util
sys.path.insert(0, "src/pycsl")
spec = importlib.util.spec_from_file_location("m5real", "src/pycsl/frontend/Module5_IREmitter.py")
m = importlib.util.module_from_spec(spec)
# need frontend package importable for its relative imports
import frontend
spec.loader.exec_module(m)
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
node = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=="IRScanner"][0]
em = m.PyCSLToJSONEmitter.__new__(m.PyCSLToJSONEmitter)
import ast as topast
print("module ast is top ast:", m.ast is topast)
r = em._collect_class_str_set_constants(node, set())
print("result:", r)
