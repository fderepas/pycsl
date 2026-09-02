import ast, os, re, sys
MIRROR="src/self-annotate/src"; LIVE="src/pycsl"
def trusted_names(path):
    names=[]; src=open(path).read().splitlines()
    for i,l in enumerate(src):
        if '#@ \\trusted' in l:
            for j in range(i, min(i+6,len(src))):
                m=re.match(r'\s*def (\w+)', src[j])
                if m: names.append(m.group(1)); break
    return names
def live_body(livepath, fname):
    try: s=open(livepath).read(); tree=ast.parse(s)
    except: return None
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==fname:
            try: return ast.get_source_segment(s, node)
            except: return None
    return None
files=sys.argv[1:]
for rel in files:
    mpath=os.path.join(MIRROR,rel); lpath=os.path.join(LIVE,rel)
    if not os.path.exists(lpath): 
        print(f"# NO LIVE {rel}"); continue
    for name in trusted_names(mpath):
        body=live_body(lpath,name)
        if body is None: print(f"{rel}::{name} NOLIVE"); continue
        nl=len([l for l in body.splitlines() if l.strip()])
        # first line of logic
        print(f"{rel}::{name} L{nl}")
