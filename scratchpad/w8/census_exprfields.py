"""For each Module-5 expression/statement handler, list the AST fields of the node type
it dispatches on that the handler NEVER MENTIONS. A never-mentioned field is a candidate
silent drop; each survivor must then be probed END-TO-END with a FALSE contract."""
import ast, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, 'src/pycsl')
from frontend import pure_ast as PA

src = open('src/pycsl/frontend/Module5_IREmitter.py', encoding='utf-8').read()
tree = ast.parse(src)

# handler tables
tables = {}
for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
            and node.target.id in ("_PY_EXPR_HANDLERS", "_PY_STMT_HANDLERS"):
        d = node.value
        m = {}
        for k, v in zip(d.keys, d.values):
            # k is ast.Attribute  ast.Name  -> "Name"
            if isinstance(k, ast.Attribute):
                m[k.attr] = v.value
        tables[node.target.id] = m

# handler bodies
bodies = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        bodies.setdefault(node.name, []).append(node)

def mentioned(fnnodes):
    names = set()
    for fn in fnnodes:
        for n in ast.walk(fn):
            if isinstance(n, ast.Attribute):
                names.add(n.attr)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                names.add(n.value)
    return names

LOC = {"lineno", "col_offset", "end_lineno", "end_col_offset", "ctx", "type_comment",
       "kind", "type_params"}
report = []
for tname, tbl in sorted(tables.items()):
    for nodetype, handler in sorted(tbl.items()):
        spec = PA._NODE_SPEC.get(nodetype)
        if not spec:
            report.append((tname, nodetype, handler, "NO _NODE_SPEC", []))
            continue
        fields = [f for f in (spec[1] or ()) if f not in LOC]
        fns = bodies.get(handler)
        if not fns:
            report.append((tname, nodetype, handler, "HANDLER NOT FOUND", fields))
            continue
        seen = mentioned(fns)
        missing = [f for f in fields if f not in seen]
        if missing:
            report.append((tname, nodetype, handler, "UNMENTIONED", missing))

for r in report:
    print("%-20s %-16s %-28s %-18s %s" % r)
print("---")
print("candidates:", len(report))
# which node types have NO handler at all?
allexpr = [n for n, sp in PA._NODE_SPEC.items() if sp[0] == 'expr']
allstmt = [n for n, sp in PA._NODE_SPEC.items() if sp[0] == 'stmt']
print("expr node types with NO handler:", sorted(set(allexpr) - set(tables.get("_PY_EXPR_HANDLERS", {}))))
print("stmt node types with NO handler:", sorted(set(allstmt) - set(tables.get("_PY_STMT_HANDLERS", {}))))
