import ast,os,re,glob
MIRROR="src/self-annotate/src"; LIVE="src/pycsl"
def trusted_stubs(path):
    lines=open(path).read().splitlines(); res=[]
    for i,l in enumerate(lines):
        if re.search(r'#@ \\trusted reviewer', l):
            for j in range(i+1,min(i+8,len(lines))):
                m=re.match(r'\s*def (\w+)\s*\(',lines[j])
                if m: res.append(m.group(1));break
    return res
live_idx={}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    try: tree=ast.parse(open(f).read())
    except: continue
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef): live_idx.setdefault(n.name,[]).append((f,n))
def bsrc(f,n): return "\n".join(open(f).read().splitlines()[n.lineno-1:n.end_lineno])
STROP=re.compile(r'startswith|endswith|\.split|\.replace|\.lower|\.upper|\.strip|\.join|\.partition|\.rsplit|== ["\']|!= ["\']| in \(')
for mf in sorted(glob.glob(MIRROR+"/**/*.py",recursive=True)):
    mb=os.path.basename(mf)
    for name in trusted_stubs(mf):
        same=[c for c in live_idx.get(name,[]) if os.path.basename(c[0])==mb]
        if not same: continue
        f,n=same[0]; b=bsrc(f,n)
        args=[a.arg for a in n.args.args]
        # first non-self param str-typed
        params=n.args.args
        strparam=False
        for a in params:
            if a.arg=="self": continue
            if a.annotation is not None and ast.unparse(a.annotation)=="str": strparam=True
            break
        if not strparam: continue
        selfstate='getattr(self' in b or re.search(r'self\._\w+\[',b)
        nested=bool(re.search(r'\n\s+def ',b))
        ret=ast.unparse(n.returns) if n.returns else "?"
        nl=n.end_lineno-n.lineno
        if STROP.search(b) and not nested and nl<=30:
            flag=" SELFSTATE" if selfstate else ""
            print(f"{mb}::{name} ret={ret} lines={nl}{flag}")
