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
BAD=('re.','ast.','os.','open(','print(','subprocess','getattr','self._','copy.','sorted(','eval(','.walk','type(')
GOODP=('str','int','bool','float')
def parms_ok(node):
    for a in node.args.args:
        if a.arg=="self": continue
        ann=a.annotation
        if ann is None: return False
        t=ast.unparse(ann)
        # allow str/int/bool/List[str]/Optional[str]/Set[str]
        if not re.match(r'^(str|int|bool|float|List\[str\]|Set\[str\]|Optional\[str\]|Tuple\[str.*\]|frozenset)$', t):
            return False
    return True
for root,_,files in os.walk(MIRROR):
    for fn in files:
        if not fn.endswith(".py"): continue
        mpath=os.path.join(root,fn); rel=os.path.relpath(mpath,MIRROR)
        lpath=os.path.join(LIVE,rel)
        if not os.path.exists(lpath): continue
        for name in trusted_names(mpath):
            node,s=node_of(lpath,name)
            if node is None: continue
            if not node.args.args: continue
            if not parms_ok(node): continue
            body=ast.get_source_segment(s,node)
            nl=len([l for l in body.splitlines() if l.strip()])
            has_nested=any(isinstance(n,(ast.FunctionDef,ast.Lambda)) for n in ast.walk(node) if n is not node)
            if has_nested: continue
            if any(b in body for b in BAD): continue
            r=node.returns; rt=ast.unparse(r) if r else "?"
            print(f"{rel}::{name} L{nl} params=[{','.join(ast.unparse(a.annotation) for a in node.args.args if a.arg!='self')}] -> {rt}")
