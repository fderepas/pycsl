import ast, glob, os
# Broad census over the MIRROR module6_whyml tree: functions with a for-loop whose
# iterable is an UNMODELED Python literal/comprehension (tuple/list literal directly,
# a comprehension, or a Var bound to such). Categorize.
def is_str_lit(n):
    return isinstance(n,(ast.Tuple,ast.List)) and n.elts and all(
        isinstance(e,ast.Constant) and isinstance(e.value,str) for e in n.elts)
def is_any_lit(n):
    return isinstance(n,(ast.Tuple,ast.List)) and bool(n.elts)
cats={"str_lit_local":set(),"str_lit_direct":set(),"other_lit_local":set(),
      "lit_direct":set(),"comprehension":set()}
for f in glob.glob("src/self-annotate/src/module6_whyml/**/*.py",recursive=True):
    try: tree=ast.parse(open(f).read())
    except: continue
    for fn in ast.walk(tree):
        if not isinstance(fn,ast.FunctionDef): continue
        litvars={}; 
        for st in ast.walk(fn):
            if isinstance(st,ast.Assign) and is_any_lit(st.value):
                for t in st.targets:
                    if isinstance(t,ast.Name): litvars[t.id]=st.value
        for st in ast.walk(fn):
            if isinstance(st,ast.For):
                it=st.iter
                key=(fn.name,f)
                if isinstance(it,(ast.ListComp,ast.GeneratorExp,ast.SetComp)):
                    cats["comprehension"].add(key)
                elif isinstance(it,ast.Name) and it.id in litvars:
                    if is_str_lit(litvars[it.id]): cats["str_lit_local"].add(key)
                    else: cats["other_lit_local"].add(key)
                elif is_str_lit(it): cats["str_lit_direct"].add(key)
                elif is_any_lit(it): cats["lit_direct"].add(key)
for c,s in cats.items():
    print(f"{c}: {len(s)}")
    for n,f in sorted(s): print(f"    {n}")
