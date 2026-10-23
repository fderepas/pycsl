import ast, os
root="src/self-annotate/src"
FILES=["module6_whyml/functions.py","module6_whyml/expressions.py","module6_whyml/statements.py",
       "core_ir_semantic.py","module6_whyml/ir_scanner.py","module6_whyml/types.py",
       "module6_whyml/auto_trust.py","module6_whyml/generic_fold.py","module6_whyml/preamble.py"]
def trusted_lines(src):
    return set(i+1 for i,l in enumerate(src.splitlines()) if '\\trusted' in l)
for rel in FILES:
    p=os.path.join(root,rel)
    if not os.path.exists(p): continue
    src=open(p).read(); lines=src.splitlines(); tl=trusted_lines(src)
    if not tl: continue
    tree=ast.parse(src)
    print(f"\n==== {rel} ====")
    # only top-level-ish trusted funcs (skip nested rec captured by parent)
    seen=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,)):
            istrust=any(ln in tl for ln in range(max(1,node.lineno-6),node.lineno))
            if not istrust: continue
            bstart=node.lineno
            bend=max((getattr(n,'end_lineno',bstart) or bstart) for n in ast.walk(node))
            body="\n".join(lines[bstart-1:bend])
            feats=[]
            if 'isinstance(' in body and 'dict' in body: feats.append('dictrec')
            if '.values()' in body: feats.append('vals')
            if '.items()' in body: feats.append('items')
            if '_walk_dicts' in body: feats.append('walkdicts')
            if '.get(' in body: feats.append('get')
            if 'raise ' in body: feats.append('RAISE')
            # nested def?
            nd=any(isinstance(n,ast.FunctionDef) and n is not node for n in ast.walk(node))
            if nd: feats.append('NESTED-def')
            if 'getattr(self' in body or 'self._' in body: feats.append('self-state')
            # return annotation
            ret=ast.unparse(node.returns) if node.returns else '?'
            print(f"  {node.name:40} L{node.lineno:<5} ret={ret:20} {','.join(feats)}")
