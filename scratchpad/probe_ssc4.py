import ast
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
node = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=="IRScanner"][0]
field_names=set()
out={}
for child in node.body:
    target=None; value=None
    if isinstance(child, ast.Assign) and len(child.targets)==1 and isinstance(child.targets[0], ast.Name):
        target=child.targets[0].id; value=child.value
    elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
        target=child.target.id; value=child.value
    if target and "MUTAT" in target:
        print("target:", target, "value:", type(value).__name__, "in field_names:", target in field_names)
        if isinstance(value, ast.Set):
            print("  is Set, elts:", [e.value for e in value.elts])
        out[target]=[e.value for e in value.elts]
print("out:", out)
