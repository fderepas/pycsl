import ast, sys, os, re, json
R = "/home/fabrice/git/pycsl-cv5"
def find(tree, qn):
    parts = qn.split("."); out = []
    def walk(n, pre):
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = pre + [c.name]
                if q == parts: out.append(c)
                walk(c, q)
            else:
                walk(c, pre)
    walk(tree, []); return out
res = {}
for l in open(R + "/getting-better/trusted-reasons.tsv"):
    if l.startswith("#") or l.startswith("file\t") or not l.strip(): continue
    rel, qn = l.split("\t")[:2]
    p = R + "/src/pycsl/" + rel
    if not os.path.exists(p): continue
    src = open(p).read(); t = ast.parse(src)
    f = find(t, qn)
    if not f: continue
    seg = ast.get_source_segment(src, f[0]) or ""
    hits = set()
    doc = set(id(x.value) for x in ast.walk(f[0]) if isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant))
    for n in ast.walk(f[0]):
        if id(n) in doc: continue
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            s = n.value
            if any(ord(ch) > 127 for ch in s): hits.add("nonascii")
            if any(ch in s for ch in "\n\t\"\\\r"): hits.add("escape")
    if hits: res["%s::%s" % (rel, qn)] = sorted(hits)
json.dump(res, open(os.path.dirname(os.path.abspath(__file__)) + "/litscan.json", "w"), indent=1)
print(len(res))
