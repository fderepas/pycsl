import ast, os, re
ROOT="/home/fabrice/git/pycsl"; MIRROR=os.path.join(ROOT,"src/self-annotate/src")
def trusted_names(path):
    src=open(path).read().split("\n"); out=set()
    for i,l in enumerate(src):
        if re.match(r'^\s*#@\s*\\trusted\b', l):
            for j in range(i+1,min(i+40,len(src))):
                m=re.match(r'^\s*def\s+(\w+)\s*\(',src[j])
                if m: out.add(m.group(1)); break
    return out
tot=0; res={}
for dp,dn,fn in os.walk(MIRROR):
    for f in fn:
        if not f.endswith(".py"): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,MIRROR)
        try: t=ast.parse(open(p).read())
        except Exception: continue
        tr=trusted_names(p)
        for n in ast.walk(t):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name not in tr:
                for sub in ast.walk(n):
                    if isinstance(sub,ast.BoolOp) and isinstance(sub.op,ast.Or):
                        last=sub.values[-1]
                        if isinstance(last,(ast.List,ast.Dict)) and not (getattr(last,'elts',None) or getattr(last,'keys',None)):
                            res.setdefault(rel,set()).add((n.name, sub.lineno)); break
for k in sorted(res):
    print(k, sorted(res[k]))
    tot+=len(res[k])
print("CONVERTED methods containing `or []`/`or {}`:", tot)
