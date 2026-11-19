import ast, sys, os, collections
roots = sys.argv[1:]
forms = collections.Counter()
examples = collections.defaultdict(list)
def desc(e):
    if e is None: return "<none>"
    c = e.__class__.__name__
    if c == "Call":
        f = e.func
        if isinstance(f, ast.Name): return "Call(Name %s)" % f.id
        if isinstance(f, ast.Attribute):
            base = f.value
            if isinstance(base, ast.Name): return "Call(Attr %s.%s)" % (base.id, f.attr)
            return "Call(Attr ?.%s)" % f.attr
        return "Call(%s)" % f.__class__.__name__
    if c == "Name": return "Name(%s)" % e.id
    if c == "Attribute": return "Attribute(.%s)" % e.attr
    return c
for root in roots:
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git','__pycache__')]
        for f in fn:
            if not f.endswith('.py'): continue
            p = os.path.join(dp, f)
            try: t = ast.parse(open(p, encoding='utf-8', errors='replace').read())
            except Exception: continue
            for n in ast.walk(t):
                if isinstance(n, (ast.With, ast.AsyncWith)):
                    for it in n.items:
                        d = desc(it.context_expr)
                        has_as = it.optional_vars is not None
                        key = (d, has_as)
                        forms[key] += 1
                        if len(examples[key]) < 3: examples[key].append("%s:%d" % (p, n.lineno))
for (d, has_as), c in forms.most_common():
    print("%5d  as=%-5s %-40s  %s" % (c, has_as, d, examples[(d,has_as)][0]))
