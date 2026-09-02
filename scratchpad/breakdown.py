rows=[l.split("\t") for l in open("scratchpad/classified.txt").read().strip().split("\n")]
stubs={}
for l in open("scratchpad/stublist.txt").read().strip().split("\n"):
    p,n,ln=l.split("\t"); stubs[n]=(p,ln)
from collections import defaultdict
PARSER={"pure_ast.py","Module2_Parser.py"}
buckets=defaultdict(list)
for cat,flags,name,lp in rows:
    mfile=stubs[name][0].split("/")[-1]
    if not cat.startswith("RET"): continue
    kinds=cat[4:]
    key=(kinds,flags,mfile in PARSER)
    buckets[key].append(name)
print("=== RET stubs: (kinds | flags | parser) : count ===")
for k in sorted(buckets, key=lambda k:-len(buckets[k])):
    kinds,flags,parser=k
    ex=",".join(buckets[k][:4])
    print(f"{len(buckets[k]):3}  [{kinds}] flags=[{flags}] {'PARSER' if parser else ''}  ex: {ex}")
