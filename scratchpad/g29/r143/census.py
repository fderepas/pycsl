"""Route #143 census: importers that bind a name free in an imported contract."""
import ast, os, sys, json, glob, subprocess
ROOT = "/home/fabrice/git/pycsl"
sys.path.insert(0, ROOT + "/src/pycsl")
os.chdir(ROOT)
from frontend import ir_resolve as R

files = []
for pat in ["src/pycsl_lib/**/*.py", "test-suite/corpus/pycsl-reference/**/*.py",
            "test-suite/corpus/python-reference/**/*.py", "src/self-annotate/src/**/*.py"]:
    files += glob.glob(pat, recursive=True)
files = sorted(set(files))

def top_bindings(tree):
    b = set()
    for st in tree.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b.add(st.name)
        elif isinstance(st, ast.Assign):
            for t in st.targets:
                for n in ast.walk(t):
                    if isinstance(n, ast.Name): b.add(n.id)
        elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
            b.add(st.target.id)
    return b

deps = {}   # resolved dep path -> list of (importer, kind, names)
imp_info = {}
for f in files:
    try:
        tree = ast.parse(open(f).read())
    except Exception:
        continue
    own = top_bindings(tree)
    imported_same = {}
    recs = []
    for st in ast.walk(tree):
        if isinstance(st, ast.ImportFrom) and st.module is not None or (isinstance(st, ast.ImportFrom) and st.level):
            try:
                res = R._resolve_module_path(st.module or "", st.level, os.path.abspath(f))
            except Exception as e:
                res = None
            if res:
                names = [(a.asname or a.name, a.name) for a in st.names]
                recs.append((os.path.abspath(res), "from", names))
        elif isinstance(st, ast.Import):
            for a in st.names:
                try:
                    res = R._resolve_module_path(a.name, 0, os.path.abspath(f))
                except Exception:
                    res = None
                if res:
                    recs.append((os.path.abspath(res), "import", [(a.asname or a.name, a.name)]))
    if recs:
        imp_info[f] = (own, recs)
        for res, kind, names in recs:
            deps.setdefault(res, []).append(f)

print("importers:", len(imp_info), "deps:", len(deps), file=sys.stderr)

def free_names(node, acc):
    if isinstance(node, dict):
        t = node.get("type")
        if t == "Var" and isinstance(node.get("name"), str): acc.add(node["name"])
        if t == "Call" and isinstance(node.get("func"), str): acc.add(node["func"])
        for v in node.values(): free_names(v, acc)
    elif isinstance(node, list):
        for v in node: free_names(v, acc)

dep_free = {}
for d in sorted(deps):
    r = subprocess.run([ROOT + "/.venv/bin/python3", "bin/pycsl-ir-dump.py", d], capture_output=True, text=True)
    if r.returncode != 0:
        dep_free[d] = None; continue
    ir = json.loads(r.stdout)
    fr = {}
    for fn in ir.get("functions", []):
        params = {p.get("name") if isinstance(p, dict) else p for p in (fn.get("params") or fn.get("formal_params") or [])}
        acc = set()
        free_names(fn.get("contracts", {}), acc)
        acc -= params; acc -= {"self", "result", "\\result"}
        if acc: fr[fn["name"]] = sorted(acc)
    dep_free[d] = fr

hits = []
for f, (own, recs) in imp_info.items():
    for res, kind, names in recs:
        fr = dep_free.get(res)
        if not fr: continue
        imported_locals = {l for r2, k2, ns in recs if r2 == res for l, _ in ns}
        for fname, fv in fr.items():
            clash = [n for n in fv if n in own and n not in imported_locals]
            if clash:
                hits.append((f, os.path.relpath(res, ROOT), kind, fname, clash))
json.dump({"dep_free": {os.path.relpath(k, ROOT): v for k, v in dep_free.items()}, "hits": hits},
          open(ROOT + "/scratchpad/g29/r143/census.json", "w"), indent=1)
print("hits:", len(hits))
for h in hits[:80]: print(h)
