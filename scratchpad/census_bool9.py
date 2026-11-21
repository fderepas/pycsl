import ast,os,re
MIRROR="src/self-annotate/src"; LIVE="src/pycsl"
def trusted_names(path):
    names=[]; src=open(path).read().splitlines()
    for i,l in enumerate(src):
        if '#@ \\trusted' in l:
            for j in range(i,min(i+6,len(src))):
                m=re.match(r'\s*def (\w+)',src[j])
                if m: names.append(m.group(1)); break
    return names
def node_of(livepath,fname):
    try: s=open(livepath).read(); tree=ast.parse(s)
    except: return None,None
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==fname:
            return node,s
    return None,None
def is_bool_ret(node):
    r=node.returns
    if isinstance(r,ast.Name) and r.id=="bool": return True
    return False
for root,_,files in os.walk(MIRROR):
    for fn in files:
        if not fn.endswith(".py"): continue
        mpath=os.path.join(root,fn); rel=os.path.relpath(mpath,MIRROR)
        lpath=os.path.join(LIVE,rel)
        if not os.path.exists(lpath): continue
        for name in trusted_names(mpath):
            node,s=node_of(lpath,name)
            if node is None: continue
            if not is_bool_ret(node): continue
            body=ast.get_source_segment(s,node)
            nl=len([l for l in body.splitlines() if l.strip()])
            # no nested def, no comprehension-with-call complexity
            has_nested=any(isinstance(n,(ast.FunctionDef,ast.Lambda)) for n in ast.walk(node) if n is not node)
            src_txt=body
            strop = any(k in src_txt for k in ('.startswith','.endswith','.lower','.upper','==','!=',' in '))
            if nl<=14 and not has_nested and strop:
                print(f"{rel}::{name} L{nl}")
