"""Port one \trusted _Unparser method from the LIVE emitter into the mirror,
dropping its `#@ \trusted` line and copying the live body verbatim."""
import ast, sys, re
MIR='src/self-annotate/src/frontend/pure_ast.py'
LIVE='src/pycsl/frontend/pure_ast.py'

def port(name):
    ms=open(MIR).read(); ls=open(LIVE).read()
    ml=ms.split('\n'); ll=ls.split('\n')
    mt=ast.parse(ms); lt=ast.parse(ls)
    mc=[n for n in mt.body if isinstance(n,ast.ClassDef) and n.name=='_Unparser'][0]
    lc=[n for n in lt.body if isinstance(n,ast.ClassDef) and n.name=='_Unparser'][0]
    mm=[f for f in mc.body if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name==name]
    lm=[f for f in lc.body if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name==name]
    if not mm or not lm: return f"NOT FOUND {name}"
    mm, lm = mm[0], lm[0]
    # mirror def span (incl decorators)
    mstart = min([d.lineno for d in mm.decorator_list] + [mm.lineno]) - 1
    mend = mm.end_lineno
    # find the trusted annotation line above
    j = mstart-1; tline=None
    while j>=0 and (ml[j].strip().startswith('#@') or ml[j].strip().startswith('@') or ml[j].strip().startswith('#')):
        if '\\trusted' in ml[j]: tline=j
        j-=1
    if tline is None: return f"NOT TRUSTED {name}"
    lstart = min([d.lineno for d in lm.decorator_list] + [lm.lineno]) - 1
    body = ll[lstart:lm.end_lineno]
    new = ml[:tline] + ml[tline+1:mstart] + body + ml[mend:]
    open(MIR,'w').write('\n'.join(new))
    return f"ported {name}"

for n in sys.argv[1:]:
    print(port(n))
