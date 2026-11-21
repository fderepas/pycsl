import ast, os
root="src/pycsl"
trusted={}
with open("/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/trusted_fns.txt") as fh:
    for line in fh:
        mf,fn=line.strip().split("\t")
        rel=mf.replace("src/self-annotate/src/","")
        trusted.setdefault(rel,set()).add(fn)
# markers that mean NOT tractable
WALL=[".items()",".values()",".keys()",".split(",".partition(",".rsplit(",".join(",".isidentifier",
      "subprocess","Path(","open(",".read(",".write(","os.",".hexdigest",".format(","f\"","f'",
      "sorted(","re.","json.","hashlib","tempfile","self.","sertop","__"]
rows=[]
for rel,fns in trusted.items():
    live=os.path.join(root,rel)
    if not os.path.exists(live): continue
    src=open(live).read()
    try: tree=ast.parse(src)
    except: continue
    lines=src.splitlines()
    def scan(container):
        for node in container:
            if isinstance(node,ast.FunctionDef) and node.name in fns:
                a=node.args.args
                if a and a[0].arg in ("self","cls"): continue
                s,e=node.lineno,node.end_lineno
                body="\n".join(lines[s-1:e])
                # remove docstring/comment lines for wall check
                code="\n".join(l for l in lines[s-1:e] if not l.strip().startswith("#"))
                walls=[w for w in WALL if w in code]
                nl=e-s+1
                if not walls:
                    rows.append((nl,rel,node.name,s,e))
    scan(tree.body)
rows.sort()
for nl,rel,fn,s,e in rows[:50]:
    print(f"nl={nl:2d} {rel}::{fn} L{s}-{e}")
print("TOTAL wall-free module-level trusted funcs:",len(rows))
