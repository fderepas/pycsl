import ast, os, re, glob

MIRROR="src/self-annotate/src"
LIVE="src/pycsl"

# Collect trusted stub qualnames per mirror file
def trusted_stubs(path):
    src=open(path).read()
    lines=src.splitlines()
    res=[]
    for i,l in enumerate(lines):
        if re.search(r'#@ \\trusted reviewer', l):
            # find next def
            for j in range(i+1, min(i+8, len(lines))):
                m=re.match(r'\s*def (\w+)\s*\(', lines[j])
                if m:
                    res.append(m.group(1)); break
    return res

# Build live method index: name -> list of (file, node)
live_idx={}
for f in glob.glob(LIVE+"/**/*.py", recursive=True):
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            live_idx.setdefault(node.name, []).append((f, node))

def body_src(f, node):
    lines=open(f).read().splitlines()
    return "\n".join(lines[node.lineno-1:node.end_lineno])

STROP=re.compile(r'startswith|endswith|\.split|\.replace|\.lower|\.upper|\.strip|\.join|\.partition|\.rsplit|== "|!= "|\.get\(')
for mf in sorted(glob.glob(MIRROR+"/**/*.py", recursive=True)):
    mfbase=os.path.basename(mf)
    for name in trusted_stubs(mf):
        cands=live_idx.get(name, [])
        # same-file match: live file basename == mirror basename
        same=[c for c in cands if os.path.basename(c[0])==mfbase]
        if not same: continue
        f,node=same[0]
        bsrc=body_src(f,node)
        # classify
        ret = ast.unparse(node.returns) if node.returns else "?"
        has_selfstate = 'getattr(self' in bsrc
        has_nesteddef = bool(re.search(r'\n\s+def ', bsrc))
        nlines=node.end_lineno-node.lineno
        strop = len(STROP.findall(bsrc))
        if strop>=1 and not has_selfstate and not has_nesteddef and ret in ("bool","str","Optional[str]") and nlines<=25:
            print(f"{mfbase}::{name} ret={ret} lines={nlines} strop={strop}")
