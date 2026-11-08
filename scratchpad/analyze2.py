import ast, os
root="src/pycsl"
trusted={}
with open("/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/trusted_fns.txt") as fh:
    for line in fh:
        mf,fn=line.strip().split("\t")
        rel=mf.replace("src/self-annotate/src/","")
        trusted.setdefault(rel,set()).add(fn)
BAD=[".items()",".values()",".keys()",".split(",".partition(",".rsplit(",".join(",".isidentifier","isinstance(",".get(","for ","while ",".append(","{",".add("]
rows=[]
for rel,fns in trusted.items():
    live=os.path.join(root,rel)
    if not os.path.exists(live): continue
    src=open(live).read(); 
    try: tree=ast.parse(src)
    except: continue
    lines=src.splitlines()
    # find module-level funcs only (not nested in class)
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name in fns:
            args=node.args.args
            if args and args[0].arg in ("self","cls"): continue
            s,e=node.lineno,node.end_lineno
            body="\n".join(lines[s-1:e])
            nl=e-s+1
            hits=sum(1 for b in BAD if b in body)
            rows.append((hits,nl,rel,node.name,s,e))
rows.sort()
for hits,nl,rel,fn,s,e in rows[:40]:
    print(f"bad={hits} nl={nl:2d} {rel}::{fn} L{s}-{e}")
