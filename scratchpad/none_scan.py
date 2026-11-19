import ast,os,re
rows=[l.split("\t") for l in open("scratchpad/classified.txt").read().strip().split("\n")]
none_names=[n for c,fl,n,lp in rows if c.startswith("NONE")]
def find(name):
    for dp,_,fs in os.walk("src/pycsl"):
        for f in fs:
            if not f.endswith(".py"):continue
            p=os.path.join(dp,f); src=open(p).read()
            if f"def {name}(" not in src:continue
            try:t=ast.parse(src)
            except:continue
            for nd in ast.walk(t):
                if isinstance(nd,(ast.FunctionDef,ast.AsyncFunctionDef)) and nd.name==name:
                    return ast.get_source_segment(src,nd)
    return None
from collections import Counter
c=Counter()
mut=[]
for n in none_names:
    seg=find(n)
    if not seg: c["nolive"]+=1; continue
    has_append=bool(re.search(r'\.append\(|\.add\(|\.update\(|\.extend\(|\[[^\]]+\]\s*=',seg))
    has_selfmut=bool(re.search(r'self\.\w+\s*=|self\.\w+\.',seg))
    has_warn="warn" in seg
    has_raise="raise " in seg
    if has_append: c["param/coll-mutate"]+=1; mut.append(n)
    elif has_selfmut: c["self-mutate"]+=1
    elif has_warn or has_raise: c["warn/raise-only"]+=1
    else: c["pure-other"]+=1
for k,v in c.most_common(): print(f"{v:4} {k}")
print("--- param/coll-mutate examples ---")
print("\n".join(mut[:30]))
