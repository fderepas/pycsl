"""Add `#@ sibling_concrete` to a named method in any mirror file."""
import ast, sys
MIR=sys.argv[1]; spec=sys.argv[2]
cls,_,name=spec.rpartition(':')
s=open(MIR).read(); L=s.split('\n')
def find(t,cls,name):
    scope=t.body
    if cls: scope=[n for n in t.body if isinstance(n,ast.ClassDef) and n.name==cls][0].body
    return [f for f in scope if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name==name][0]
f=find(ast.parse(s),cls,name)
st=min([d.lineno for d in f.decorator_list]+[f.lineno])-1
j=st-1
while j>=0 and (L[j].strip().startswith('#') or L[j].strip().startswith('@')): j-=1
blk=[x.strip() for x in L[j+1:st]]
if '#@ sibling_concrete' in blk:
    print('already', spec); sys.exit(0)
indent=' ' * (len(L[st]) - len(L[st].lstrip()))
L.insert(j+1, indent+'#@ sibling_concrete')
open(MIR,'w').write('\n'.join(L))
print('added', spec)
