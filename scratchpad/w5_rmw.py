import ast, os, re
ROOT="/home/fabrice/git/pycsl"; MIRROR=os.path.join(ROOT,"src/self-annotate/src")
MUT={"append","extend","add","update","sort","insert","clear","discard","remove","appendleft","extendleft","reverse","difference_update","intersection_update"}
def trusted_names(path):
    src=open(path).read().split("\n"); out=set()
    for i,l in enumerate(src):
        if re.match(r'^\s*#@\s*\\trusted\b', l):
            for j in range(i+1,min(i+40,len(src))):
                m=re.match(r'^\s*def\s+(\w+)\s*\(',src[j])
                if m: out.add(m.group(1)); break
    return out
# mutable_state classes
ms=set()
for dp,dn,fn in os.walk(MIRROR):
    for f in fn:
        if not f.endswith(".py"): continue
        p=os.path.join(dp,f); L=open(p).read().split("\n")
        for i,l in enumerate(L):
            if "@mutable_state" in l:
                for j in range(i,min(i+8,len(L))):
                    m=re.match(r'^\s*class\s+(\w+)',L[j])
                    if m: ms.add(m.group(1)); break
print("mutable_state classes:", sorted(ms))
res={}
for dp,dn,fn in os.walk(MIRROR):
    for f in fn:
        if not f.endswith(".py"): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,MIRROR)
        try: t=ast.parse(open(p).read())
        except Exception: continue
        tr=trusted_names(p)
        for cls in ast.walk(t):
            if not isinstance(cls,ast.ClassDef) or cls.name not in ms: continue
            for n in cls.body:
                if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
                conv = n.name not in tr
                for sub in ast.walk(n):
                    if (isinstance(sub,ast.Call) and isinstance(sub.func,ast.Attribute)
                        and sub.func.attr in MUT
                        and isinstance(sub.func.value,ast.Attribute)
                        and isinstance(sub.func.value.value,ast.Name)
                        and sub.func.value.value.id=="self"):
                        res.setdefault((rel,cls.name,conv),set()).add((n.name,sub.func.value.attr,sub.func.attr))
for k in sorted(res, key=lambda x:(x[0],x[1])):
    print(("CONV " if k[2] else "TRUS "), k[0], k[1], len(res[k]))
    for v in sorted(res[k]): print("      ", v)
