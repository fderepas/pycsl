"""Route #55 census: `if <name>:` truthiness guards on a dict/set-typed PARAM or local,
inside a @mutable_state class, split by whether the enclosing method carries a REAL
postcondition (anything other than `#@ ensures True`)."""
import ast, os, sys, re

def ensures_of(src_lines, lineno):
    """Collect `#@ ensures` lines in the contract block immediately above a def."""
    out = []
    i = lineno - 2
    while i >= 0:
        s = src_lines[i].strip()
        if s.startswith('#@') or s.startswith('#') or s == '':
            m = re.match(r'#@\s*ensures\s+(.*)', s)
            if m:
                out.append(m.group(1).strip())
            i -= 1
            continue
        break
    return out

for root in sys.argv[1:]:
    tot = triv = real = 0
    rows = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('__pycache__', '.git', '.venv')]
        for f in sorted(fn):
            if not f.endswith('.py'):
                continue
            p = os.path.join(dp, f)
            try:
                src = open(p, encoding='utf-8').read()
                tree = ast.parse(src)
            except Exception:
                continue
            lines = src.splitlines()
            for cls in ast.walk(tree):
                if not isinstance(cls, ast.ClassDef):
                    continue
                if 'mutable_state' not in ' '.join(ast.unparse(d) for d in cls.decorator_list):
                    continue
                for m in cls.body:
                    if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    ann = {a.arg: (ast.unparse(a.annotation) if a.annotation else '')
                           for a in m.args.args + m.args.kwonlyargs}
                    dictset = {k for k, v in ann.items()
                               if re.match(r'^(Dict|Set|dict|set|Mapping|FrozenSet)\b', v)}
                    if not dictset:
                        continue
                    ens = ensures_of(lines, m.lineno)
                    isreal = any(e not in ('True', 'true') for e in ens)
                    for n in ast.walk(m):
                        if isinstance(n, ast.If) and isinstance(n.test, ast.Name) \
                                and n.test.id in dictset:
                            tot += 1
                            if isreal:
                                real += 1
                                rows.append(f"REAL-ENSURES {os.path.relpath(p,root)}::{cls.name}.{m.name}:{n.lineno} if {n.test.id}: ({ens})")
                            else:
                                triv += 1
                                rows.append(f"ensures-True  {os.path.relpath(p,root)}::{cls.name}.{m.name}:{n.lineno} if {n.test.id}:")
    print(f"== {root}: {tot} bare `if <dict/set param>:` guards in @mutable_state classes — {triv} under ensures-True, {real} under a REAL postcondition")
    for r in rows[:25]:
        print("   " + r)
