import re, ast, os
lines = open("scratchpad/stublist.txt").read().strip().split("\n")
stubs = [l.split("\t") for l in lines]

def find_live_body(name):
    # search src/pycsl for `def name(` and extract body via ast per-file
    for dp,_,fs in os.walk("src/pycsl"):
        for f in fs:
            if not f.endswith(".py"): continue
            p=os.path.join(dp,f)
            try: src=open(p).read()
            except: continue
            if f"def {name}(" not in src: continue
            try: tree=ast.parse(src)
            except: continue
            for node in ast.walk(tree):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
                    seg=ast.get_source_segment(src,node)
                    if seg: return p,seg,node
    return None,None,None

def classify(name, seg, node):
    if seg is None: return "NOLIVE", ""
    body_src = seg
    # return type / returns
    returns=[]
    for n in ast.walk(node):
        if isinstance(n,ast.Return) and n.value is not None:
            returns.append(n)
    has_raise=any(isinstance(n,ast.Raise) for n in ast.walk(node))
    has_warn="warnings.warn" in body_src or "warn(" in body_src
    # detect regex
    regex = bool(re.search(r'\bre\.|_RE\b|\.match\(|\.search\(|\.finditer|re\.compile', body_src))
    fileio = bool(re.search(r'read_text|open\(|iterdir|\.glob\(|Path\(|os\.|subprocess|\.write', body_src))
    astwalk = bool(re.search(r'ast\.walk|ast\.[A-Z]\w+|isinstance\([^,]+,\s*ast\.', body_src))
    strtoint = bool(re.search(r'int\([^)]*str|int\(count|int\(\w+_str', body_src))
    # return value kind
    kinds=set()
    for r in returns:
        v=r.value
        if isinstance(v,ast.Constant):
            if v.value is None: kinds.add("None")
            elif isinstance(v.value,bool): kinds.add("bool")
            elif isinstance(v.value,int): kinds.add("int")
            elif isinstance(v.value,str): kinds.add("str")
            else: kinds.add("const")
        elif isinstance(v,(ast.List,ast.ListComp)): kinds.add("list")
        elif isinstance(v,(ast.Set,ast.SetComp)): kinds.add("set")
        elif isinstance(v,(ast.Dict,ast.DictComp)): kinds.add("dict")
        elif isinstance(v,ast.Tuple): kinds.add("tuple")
        elif isinstance(v,(ast.Compare,ast.BoolOp)): kinds.add("bool")
        elif isinstance(v,ast.Call): kinds.add("call")
        elif isinstance(v,ast.Name): kinds.add("name")
        else: kinds.add("expr")
    if not returns and not has_raise:
        cat="NONE-noreturn"
    elif not returns and has_raise:
        cat="NONE-raiseonly"
    else:
        cat="RET:"+",".join(sorted(kinds))
    flags=[]
    if regex: flags.append("regex")
    if fileio: flags.append("fileio")
    if astwalk: flags.append("ast")
    if strtoint: flags.append("str2int")
    if has_warn: flags.append("warn")
    if has_raise: flags.append("raise")
    return cat, "|".join(flags)

from collections import Counter, defaultdict
cats=Counter()
rows=[]
for p,name,ln in stubs:
    lp,seg,node=find_live_body(name)
    cat,flags=classify(name,seg,node)
    cats[cat.split(":")[0] if cat.startswith("RET") else cat]+=1
    rows.append((cat,flags,name,p,lp or "NOLIVE"))
open("scratchpad/classified.txt","w").write("\n".join(f"{c}\t{fl}\t{n}\t{lp}" for c,fl,n,p,lp in rows))
print("=== CATEGORY COUNTS ===")
for c,n in cats.most_common(): print(f"{n:4} {c}")
