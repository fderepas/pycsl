import ast, os, re, sys

MIRROR="src/self-annotate/src"
LIVE="src/pycsl"

def trusted_names(path):
    names=[]
    src=open(path).read().splitlines()
    for i,l in enumerate(src):
        if '#@ \\trusted' in l:
            # find next def
            for j in range(i, min(i+6,len(src))):
                m=re.match(r'\s*def (\w+)', src[j])
                if m: names.append(m.group(1)); break
    return names

def live_body(livepath, fname):
    try: tree=ast.parse(open(livepath).read())
    except: return None
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==fname:
            try: return ast.get_source_segment(open(livepath).read(), node)
            except: return None
    return None

# tags
def tag(body):
    tags=[]
    if not body: return ["NOLIVE"]
    if '.startswith' in body or '.endswith' in body: tags.append("startswith")
    if '.strip(' in body or '.lstrip(' in body or '.rstrip(' in body: tags.append("strip")
    if '.split(' in body: tags.append("split")
    if '.lower()' in body or '.upper()' in body: tags.append("case")
    if '.replace(' in body: tags.append("replace")
    if re.search(r'Optional\[str\]', body): tags.append("opt_str_ann")
    nlines=len([l for l in body.splitlines() if l.strip()])
    tags.append(f"L{nlines}")
    return tags

targets = sys.argv[1:] if len(sys.argv)>1 else None
for root,_,files in os.walk(MIRROR):
    for fn in files:
        if not fn.endswith(".py"): continue
        mpath=os.path.join(root,fn)
        rel=os.path.relpath(mpath, MIRROR)
        lpath=os.path.join(LIVE, rel)
        if targets and rel not in targets and fn not in targets: continue
        if not os.path.exists(lpath): continue
        for name in trusted_names(mpath):
            body=live_body(lpath,name)
            tg=tag(body)
            strop = any(t in tg for t in ("startswith","strip","split","case","replace"))
            if strop:
                print(f"{rel}::{name}  {tg}")
