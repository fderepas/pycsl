import ast, os, re, sys
ROOT="/home/fabrice/git/pycsl"
MIRROR=os.path.join(ROOT,"src/self-annotate/src")
LIVE=os.path.join(ROOT,"src/pycsl")

def trusted_stubs(path):
    src=open(path).read().split("\n")
    out=[]
    for i,l in enumerate(src):
        if re.match(r'^\s*#@\s*\\trusted\b', l):
            # find next def
            for j in range(i+1, min(i+40,len(src))):
                m=re.match(r'^\s*def\s+(\w+)\s*\(', src[j])
                if m:
                    out.append(m.group(1)); break
    return out

def live_bodies(path):
    try: t=ast.parse(open(path).read())
    except Exception: return {}
    res={}
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            res.setdefault(n.name,[]).append(n)
    return res

tot=0; hits={}
for dp,dn,fn in os.walk(MIRROR):
    for f in fn:
        if not f.endswith(".py"): continue
        mp=os.path.join(dp,f)
        rel=os.path.relpath(mp,MIRROR)
        lp=os.path.join(LIVE,rel)
        if not os.path.exists(lp):
            # frontend/X -> pycsl/frontend/X ; try basename search
            continue
        stubs=set(trusted_stubs(mp))
        if not stubs: continue
        lb=live_bodies(lp)
        for s in stubs:
            for node in lb.get(s,[]):
                srcseg=ast.get_source_segment(open(lp).read(), node) or ""
                for sub in ast.walk(node):
                    if isinstance(sub,ast.BoolOp) and isinstance(sub.op,ast.Or):
                        vs=sub.values
                        if len(vs)>=2 and isinstance(vs[-1],(ast.List,ast.Dict)) and not (getattr(vs[-1],'elts',None) or getattr(vs[-1],'keys',None)):
                            hits.setdefault(rel,set()).add(s)
                            break
tot=sum(len(v) for v in hits.values())
for k in sorted(hits): print(f"{len(hits[k]):3d}  {k}: {sorted(hits[k])}")
print("TOTAL stubs with `or []`/`or {}`:", tot)
