import ast, sys
MIR='src/self-annotate/src/frontend/pure_ast.py'; LIVE='src/pycsl/frontend/pure_ast.py'
spec=sys.argv[1]  # Class:name or name
cls,_,name = spec.rpartition(':')
ms=open(MIR).read(); ls=open(LIVE).read()
ml=ms.split('\n'); ll=ls.split('\n')
def find(tree, cls, name):
    scope = tree.body
    if cls:
        scope=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls][0].body
    return [f for f in scope if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name==name][0]
mm=find(ast.parse(ms),cls,name); lm=find(ast.parse(ls),cls,name)
mstart=min([d.lineno for d in mm.decorator_list]+[mm.lineno])-1; mend=mm.end_lineno
j=mstart-1; tline=None
while j>=0 and (ml[j].strip().startswith('#@') or ml[j].strip().startswith('@') or ml[j].strip().startswith('#')):
    if '\\trusted' in ml[j]: tline=j
    j-=1
assert tline is not None, "no trusted line for "+spec
lstart=min([d.lineno for d in lm.decorator_list]+[lm.lineno])-1
open(MIR,'w').write('\n'.join(ml[:tline]+ml[tline+1:mstart]+ll[lstart:lm.end_lineno]+ml[mend:]))
print('ported', spec)
