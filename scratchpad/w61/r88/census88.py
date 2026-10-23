import ast, sys, os, collections
roots = {
 'corpus/pycsl-ref':'test-suite/corpus/pycsl-reference',
 'corpus/python-ref':'test-suite/corpus/python-reference',
 'mirror':'src/self-annotate',
 'src/pycsl':'src/pycsl',
 'src/pycsl_lib':'src/pycsl_lib',
}
tot = collections.Counter()
detail = collections.defaultdict(list)
for label, root in roots.items():
    if not os.path.isdir(root): print('MISSING', root); continue
    n_files=0
    for dp,_,fns in os.walk(root):
        for fn in fns:
            if not fn.endswith('.py'): continue
            p=os.path.join(dp,fn); n_files+=1
            try: t=ast.parse(open(p, encoding='utf-8', errors='replace').read())
            except Exception: tot[label+' PARSE-FAIL']+=1; continue
            for cls in [x for x in ast.walk(t) if isinstance(x, ast.ClassDef)]:
                for init in [c for c in cls.body if isinstance(c, ast.FunctionDef) and c.name=='__init__']:
                    stores = collections.Counter()   # field -> count of Assign/AnnAssign stores (anywhere)
                    top_stores = collections.Counter()
                    aug = set()
                    topids = {id(s) for s in init.body}
                    for st in ast.walk(init):
                        tg=None
                        if isinstance(st, ast.Assign) and len(st.targets)==1: tg=st.targets[0]
                        elif isinstance(st, ast.AnnAssign): tg=st.target
                        elif isinstance(st, ast.AugAssign): 
                            t2=st.target
                            if isinstance(t2, ast.Attribute) and isinstance(t2.value, ast.Name) and t2.value.id=='self':
                                aug.add(t2.attr)
                            continue
                        if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id=='self':
                            stores[tg.attr]+=1
                            if id(st) in topids: top_stores[tg.attr]+=1
                    multi_top = [f for f,c in top_stores.items() if c>1]
                    multi_any = [f for f,c in stores.items() if c>1]
                    if multi_top:
                        tot[label+' MULTI-TOP-STORE']+=len(multi_top)
                        detail[label+' MULTI-TOP'].append((p, cls.name, multi_top))
                    if aug:
                        tot[label+' AUGASSIGN-FIELD']+=len(aug)
                        detail[label+' AUG'].append((p, cls.name, sorted(aug)))
                    only_nested = [f for f in multi_any if f not in multi_top]
                    if only_nested:
                        tot[label+' MULTI-INCL-NESTED-ONLY']+=len(only_nested)
    tot[label+' FILES']=n_files
for k in sorted(tot): print(f'{tot[k]:6d}  {k}')
print()
for k in sorted(detail):
    print('###', k)
    for p,c,fs in detail[k][:40]: print('   ', p, c, fs)
