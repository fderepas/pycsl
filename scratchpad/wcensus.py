import ast, os, sys
root="src/self-annotate/src"
def trusted_lines(src):
    return set(i+1 for i,l in enumerate(src.splitlines()) if '\\trusted' in l)
hits=[]
for dp,_,fs in os.walk(root):
    for fn in fs:
        if not fn.endswith(".py"): continue
        p=os.path.join(dp,fn)
        src=open(p).read()
        tl=trusted_lines(src)
        if not tl: continue
        try: tree=ast.parse(src)
        except: continue
        # map each function to whether a trusted line precedes it (in decorator/comment region)
        lines=src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                # trusted marker is a comment line just above def, within a few lines
                istrust=False
                for ln in range(max(1,node.lineno-6),node.lineno):
                    if ln in tl: istrust=True
                if not istrust: continue
                # body text
                bstart=node.body[0].lineno if node.body else node.lineno
                bend=max((getattr(n,'end_lineno',bstart) or bstart) for n in ast.walk(node))
                body="\n".join(lines[node.lineno-1:bend])
                uses_items='.items()' in body
                uses_values='.values()' in body
                if uses_items or uses_values:
                    tag=('items' if uses_items else '')+('/values' if uses_values else '')
                    hits.append((p,node.name,node.lineno,tag,bend-node.lineno))
for h in sorted(hits):
    print(f"{h[0].split('/',2)[2]:55} {h[1]:35} L{h[2]:<5} {h[3]:12} ~{h[4]}L")
print("TOTAL items/values trusted stubs:",len(hits))
