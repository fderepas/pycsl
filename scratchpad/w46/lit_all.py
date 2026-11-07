import ast, os
CONSTS = {"true","false","0","1","()","","0.0","unit"}
ROOT="src/pycsl/module6_whyml"
rows=[]
for dp,dn,fn in os.walk(ROOT):
    for f in sorted(fn):
        if not f.endswith(".py"): continue
        p=os.path.join(dp,f)
        t=ast.parse(open(p,encoding="utf-8").read())
        for fu in ast.walk(t):
            if not isinstance(fu,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
            for n in ast.walk(fu):
                if (isinstance(n,ast.Return) and isinstance(n.value,ast.Constant)
                        and isinstance(n.value.value,str)
                        and n.value.value.strip() in CONSTS):
                    rows.append((p,n.lineno,fu.name,n.value.value.strip()))
from collections import Counter
c=Counter(r[3] for r in rows)
print("%d constant-return site(s) in %d function(s)" % (len(rows), len(set(r[2] for r in rows))))
for lit,k in c.most_common():
    print("\n--- %r : %d ---" % (lit,k))
    for p,ln,nm,_ in rows:
        if _==lit: print("   %s:%d  %s" % (p,ln,nm))
