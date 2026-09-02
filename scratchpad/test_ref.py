import ast
src=open("src/pycsl/module6_whyml/expressions.py").read()
tree=ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name=="_recognize_field_decode_idiom":
        print("FOUND ref at", node.lineno)
        import ast as A
        print(A.dump(node.body[0]) if node.body else "empty")

# reuse has_idiom
import ast
def has_idiom(fn):
    guarded=set()
    for node in ast.walk(fn):
        if isinstance(node,ast.If):
            t=node.test
            if isinstance(t,ast.Compare) and len(t.ops)==1 and isinstance(t.ops[0],ast.Is) and isinstance(t.comparators[0],ast.Constant) and t.comparators[0].value is None and isinstance(t.left,ast.Name):
                for b in node.body:
                    if isinstance(b,ast.Return) and (b.value is None or (isinstance(b.value,ast.Constant) and b.value.value is None)):
                        guarded.add(t.left.id)
    unpacked=set()
    for node in ast.walk(fn):
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],(ast.Tuple,ast.List)) and isinstance(node.value,ast.Name) and node.value.id in guarded:
            unpacked.add(node.value.id)
    return guarded&unpacked
for node in ast.walk(tree):
    if isinstance(node,(ast.FunctionDef,)) and node.name=="_recognize_field_decode_idiom":
        print("DETECTOR on ref:", has_idiom(node))
