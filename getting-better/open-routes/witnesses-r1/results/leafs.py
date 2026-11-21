import ast, sys, json
# leafs.py <file> <out.json> fn...: insert `#@ assert 1 == 2` at the first statement of every LEAF block
# (an if/elif/else/for/while body containing no compound statement) of each named PyCSLToJSONEmitter method
p, out = sys.argv[1:3]; fns = set(sys.argv[3:])
src = open(p).read(); L = src.split("\n"); t = ast.parse(src)
COMP = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)
ins = []
for c in t.body:
    if isinstance(c, ast.ClassDef) and c.name == "PyCSLToJSONEmitter":
        for f in c.body:
            if isinstance(f, ast.FunctionDef) and f.name in fns:
                for n in ast.walk(f):
                    blocks = []
                    if isinstance(n, (ast.If, ast.For, ast.While)):
                        blocks = [n.body] + ([n.orelse] if n.orelse and not (len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If)) else [])
                    for b in blocks:
                        if b and not any(isinstance(s, COMP) for s in b):
                            ins.append((b[0].lineno, b[0].col_offset, f.name))
ins.sort(reverse=True)
for ln, col, fn in ins:
    L.insert(ln - 1, " " * col + "#@ assert 1 == 2")
open(p, "w").write("\n".join(L))
json.dump(sorted(ins), open(out, "w"))
from collections import Counter
print(Counter(fn for _, _, fn in ins))
