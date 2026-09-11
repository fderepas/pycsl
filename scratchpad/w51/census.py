"""Census: `X is None` / `X is not None` tests, classified by what X is.
Classes: LOCAL (X is a Var assigned somewhere in the enclosing function),
PARAM (X is a Var that is a parameter and never assigned), FIELD (X is self.<f>),
OTHER (subscript, call, nested attribute, ...)."""
import ast, sys, os, collections

def scan(root):
    out = collections.Counter()
    sites = collections.defaultdict(list)
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('__pycache__', '.git')]
        for f in fn:
            if not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            try:
                tree = ast.parse(open(p, encoding='utf-8').read())
            except Exception:
                continue
            for fn_node in ast.walk(tree):
                if not isinstance(fn_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                params = {a.arg for a in fn_node.args.args + fn_node.args.kwonlyargs}
                assigned = set()
                for n in ast.walk(fn_node):
                    if isinstance(n, ast.Assign):
                        for t in n.targets:
                            if isinstance(t, ast.Name):
                                assigned.add(t.id)
                    elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and isinstance(n.target, ast.Name):
                        assigned.add(n.target.id)
                    elif isinstance(n, ast.For) and isinstance(n.target, ast.Name):
                        assigned.add(n.target.id)
                    elif isinstance(n, ast.withitem) and isinstance(n.optional_vars, ast.Name):
                        assigned.add(n.optional_vars.id)
                for n in ast.walk(fn_node):
                    if not isinstance(n, ast.Compare) or len(n.ops) != 1:
                        continue
                    if not isinstance(n.ops[0], (ast.Is, ast.IsNot)):
                        continue
                    c = n.comparators[0]
                    if not (isinstance(c, ast.Constant) and c.value is None):
                        continue
                    L = n.left
                    if isinstance(L, ast.Name):
                        if L.id in assigned:
                            k = 'LOCAL'
                        elif L.id in params:
                            k = 'PARAM'
                        else:
                            k = 'FREE'
                    elif (isinstance(L, ast.Attribute) and isinstance(L.value, ast.Name)
                          and L.value.id == 'self'):
                        k = 'FIELD'
                    else:
                        k = 'OTHER'
                    out[k] += 1
                    sites[k].append(f"{os.path.relpath(p, root)}::{fn_node.name}:{n.lineno}")
    return out, sites

for root in sys.argv[1:]:
    o, s = scan(root)
    print(f"== {root}: {sum(o.values())} `is None` tests")
    for k in ('LOCAL', 'PARAM', 'FIELD', 'FREE', 'OTHER'):
        print(f"   {k:6} {o[k]}")
    for k in ('PARAM', 'FIELD'):
        for x in s[k][:6]:
            print(f"      {k}: {x}")
