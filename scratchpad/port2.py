"""Generic: port a \trusted mirror stub from the LIVE emitter. Usage:
   port2.py <mirror.py> Class:method [Class:method ...]   (use '-' for module-level)"""
import ast, sys, os
MROOT='src/self-annotate/src'; LROOT='src/pycsl'
def find(tree, cls, name):
    if cls in (None,'-','<module>'):
        for n in tree.body:
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name: return n
        return None
    for n in tree.body:
        if isinstance(n,ast.ClassDef) and n.name==cls:
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name==name: return m
    return None
def port(mir, cls, name):
    live=os.path.join(LROOT, os.path.relpath(mir, MROOT))
    ms=open(mir).read(); ls=open(live).read()
    ml=ms.split('\n'); ll=ls.split('\n')
    m=find(ast.parse(ms), cls, name); l=find(ast.parse(ls), cls, name)
    if m is None or l is None: return f"NOT FOUND {cls}.{name}"
    ind=len(ml[m.lineno-1])-len(ml[m.lineno-1].lstrip())
    mstart=min([d.lineno for d in m.decorator_list]+[m.lineno])-1
    j=mstart-1; tline=None
    while j>=0 and ml[j].strip().startswith(('#@','#','@')):
        if '\\trusted' in ml[j]: tline=j
        j-=1
    if tline is None: return f"NOT TRUSTED {cls}.{name}"
    lstart=min([d.lineno for d in l.decorator_list]+[l.lineno])-1
    body=ll[lstart:l.end_lineno]
    new=ml[:tline]+ml[tline+1:mstart]+body+ml[m.end_lineno:]
    open(mir,'w').write('\n'.join(new))
    return f"ported {cls}.{name}"
mir=sys.argv[1]
for a in sys.argv[2:]:
    c,n = a.split(':') if ':' in a else (None,a)
    print(port(mir, c, n))
