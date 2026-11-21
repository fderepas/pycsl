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
# find functions with a Call to .strip/.lower/.upper/.replace in a boolean/if/while test or bool-op position
STRM={'strip','lstrip','rstrip','lower','upper','replace'}
def is_strcall(n):
    return (isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in STRM)
for root,_,files in os.walk(MIRROR):
    for fn in files:
        if not fn.endswith(".py"): continue
        mpath=os.path.join(root,fn); rel=os.path.relpath(mpath,MIRROR)
        lpath=os.path.join(LIVE,rel)
        if not os.path.exists(lpath): continue
        for name in trusted_names(mpath):
            node,s=node_of(lpath,name)
            if node is None: continue
            hits=[]
            for n in ast.walk(node):
                # test positions
                if isinstance(n,(ast.If,ast.While)) and is_strcall(n.test): hits.append("if/while-strcall")
                if isinstance(n,ast.BoolOp):
                    for v in n.values:
                        if is_strcall(v): hits.append("boolop-strcall")
                if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.Not) and is_strcall(n.operand): hits.append("not-strcall")
            if hits:
                print(f"{rel}::{name}  {set(hits)}")
