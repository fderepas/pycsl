"""Transitive field-coverage census: for each Module-5 handler, walk the handler AND every
same-module function/method it calls (to depth D), and report AST fields of the dispatched
node type that are never mentioned anywhere in that closure."""
import ast, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, 'src/pycsl')
from frontend import pure_ast as PA

PATH = 'src/pycsl/frontend/Module5_IREmitter.py'
src = open(PATH, encoding='utf-8').read()
tree = ast.parse(src)

funcs = {}
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef):
        funcs.setdefault(n.name, []).append(n)

tables = {}
for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
            and node.target.id in ("_PY_EXPR_HANDLERS", "_PY_STMT_HANDLERS"):
        m = {}
        for k, v in zip(node.value.keys, node.value.values):
            if isinstance(k, ast.Attribute):
                m[k.attr] = v.value
        tables[node.target.id] = m

def closure(name, depth):
    seen, frontier = set(), [(name, 0)]
    while frontier:
        nm, d = frontier.pop()
        if nm in seen or nm not in funcs or d > depth:
            continue
        seen.add(nm)
        for fn in funcs[nm]:
            for c in ast.walk(fn):
                if isinstance(c, ast.Call):
                    f = c.func
                    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                            and f.value.id == "self":
                        frontier.append((f.attr, d + 1))
                    elif isinstance(f, ast.Name):
                        frontier.append((f.id, d + 1))
    return seen

def mentioned(names):
    out = set()
    for nm in names:
        for fn in funcs.get(nm, []):
            for n in ast.walk(fn):
                if isinstance(n, ast.Attribute):
                    out.add(n.attr)
                elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                    out.add(n.value)
    return out

LOC = {"lineno", "col_offset", "end_lineno", "end_col_offset", "ctx", "type_comment",
       "kind", "type_params"}
DEPTH = int(sys.argv[1]) if len(sys.argv) > 1 else 3
hits = 0
for tname, tbl in sorted(tables.items()):
    for nodetype, handler in sorted(tbl.items()):
        spec = PA._NODE_SPEC.get(nodetype)
        if not spec:
            continue
        fields = [f for f in (spec[1] or ()) if f not in LOC]
        seen = mentioned(closure(handler, DEPTH))
        missing = [f for f in fields if f not in seen]
        if missing:
            hits += 1
            print("%-20s %-16s %-26s missing=%s" % (tname, nodetype, handler, missing))
print("--- unmentioned-field candidates at depth %d: %d" % (DEPTH, hits))
