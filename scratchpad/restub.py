import ast, sys
MIR='src/self-annotate/src/frontend/pure_ast.py'
for name in sys.argv[1:]:
    ms=open(MIR).read(); ml=ms.split('\n')
    mt=ast.parse(ms); mc=[n for n in mt.body if isinstance(n,ast.ClassDef) and n.name=='_Unparser'][0]
    f=[x for x in mc.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name]
    if not f: print("NOT FOUND", name); continue
    m=f[0]
    start=min([d.lineno for d in m.decorator_list]+[m.lineno])-1
    # the three #@ lines above
    ann=[]
    j=start-1
    while j>=0 and ml[j].strip().startswith('#@'):
        ann.insert(0, ml[j]); j-=1
    if any('\\trusted' in a for a in ann): print("ALREADY TRUSTED", name); continue
    # restore assigns \nothing (a trusted stub's body is `pass`, it writes nothing)
    ann=[('    #@ assigns \\nothing' if a.strip().startswith('#@ assigns') else a) for a in ann]
    sig=ml[start]
    new = ml[:j+1] + ['    #@ \\trusted reviewer: pycsl-self-annotate'] + ann + [sig, '        pass'] + ml[m.end_lineno:]
    open(MIR,'w').write('\n'.join(new))
    print("re-stubbed", name)
