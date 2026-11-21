"""Audit the CONVERTED mirror population for the two facade classes #32 found in the probe:
   (A) PARAM-FIELD MATERIALIZED as a fresh constant array
   (B) COMPUTED RHS ERASED TO 0
Reads the already-emitted .mlw baseline in scratchpad/w5/t2."""
import ast, os, re, sys
ROOT="/home/fabrice/git/pycsl"; MIRROR=os.path.join(ROOT,"src/self-annotate/src")
BASE=os.path.join(ROOT,"scratchpad/w5/t2")
BLK=re.compile(r"^  (let(?: rec)?(?: function)?(?: partial)?|val|with)\s+([A-Za-z0-9_']+)[^\n]*\n(?:(?!^  (?:let|val|with|type|exception|axiom|goal|lemma)\b).*\n)*", re.M)
def trusted_names(path):
    L=open(path).read().split("\n"); out=set()
    for i,l in enumerate(L):
        if re.match(r'^\s*#@\s*\\trusted\b', l):
            for j in range(i+1,min(i+40,len(L))):
                m=re.match(r'^\s*def\s+(\w+)\s*\(',L[j])
                if m: out.add(m.group(1)); break
    return out
hitsA=[]; hitsB=[]
for dp,dn,fn in os.walk(MIRROR):
    for f in sorted(fn):
        if not f.endswith(".py"): continue
        p=os.path.join(dp,f); rel=os.path.relpath(p,MIRROR)
        mlw=os.path.join(BASE, rel.replace("/","_")[:-3]+".mlw")
        if not os.path.exists(mlw): continue
        txt=open(mlw).read()
        blocks={}
        for m in BLK.finditer(txt): blocks.setdefault(m.group(2), m.group(0))
        try: t=ast.parse(open(p).read())
        except Exception: continue
        tr=trusted_names(p)
        for n in ast.walk(t):
            if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): continue
            if n.name in tr: continue
            blk=None
            for k,v in blocks.items():
                if k==n.name or k.endswith("__"+n.name): blk=v; break
            if blk is None or blk.lstrip().startswith("val"): continue
            params=[a.arg for a in n.args.args if a.arg!="self"]
            pf=sorted({(x.value.id,x.attr) for x in ast.walk(n)
                       if isinstance(x,ast.Attribute) and isinstance(x.value,ast.Name)
                       and x.value.id in params})
            mat=[f"{o}.{fl}" for o,fl in pf
                 if re.search(r"\blet %s_%s = \(?Array\.make\b"%(re.escape(o),re.escape(fl)), blk)]
            if mat: hitsA.append((rel,n.name,mat))
            er=[]
            for a in ast.walk(n):
                if not isinstance(a,ast.Assign) or len(a.targets)!=1: continue
                tg=a.targets[0]
                if not isinstance(tg,ast.Name): continue
                if not isinstance(a.value,(ast.Call,ast.Attribute,ast.Subscript,ast.ListComp,ast.DictComp,ast.SetComp,ast.GeneratorExp)): continue
                if any(isinstance(o,ast.Assign) and len(o.targets)==1 and isinstance(o.targets[0],ast.Name)
                       and o.targets[0].id==tg.id and isinstance(o.value,ast.Constant) and not o.value.value
                       for o in ast.walk(n)): continue
                if re.search(r"(?m)^\s*%s := 0\s*;?\s*$"%re.escape(tg.id), blk): er.append(tg.id)
            if er: hitsB.append((rel,n.name,sorted(set(er))))
print("=== (A) PARAM-FIELD MATERIALIZED, converted population:", len(hitsA))
for h in hitsA: print("   ",h)
print("=== (B) COMPUTED RHS ERASED TO 0, converted population:", len(hitsB))
for h in hitsB: print("   ",h)
