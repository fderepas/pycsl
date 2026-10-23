import ast
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "IRScanner":
        for child in node.body:
            if isinstance(child, (ast.Assign, ast.AnnAssign)):
                if isinstance(child, ast.AnnAssign):
                    tgt = child.target
                    val = child.value
                else:
                    tgt = child.targets[0] if len(child.targets)==1 else None
                    val = child.value
                nm = getattr(tgt, "id", None)
                if nm and "MUTAT" in nm:
                    print("FOUND", nm, "value type:", type(val).__name__, "annotation:", ast.dump(child.annotation) if isinstance(child, ast.AnnAssign) else None)
                    print("value:", ast.dump(val))
