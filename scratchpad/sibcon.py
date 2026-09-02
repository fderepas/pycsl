"""Add or remove `#@ sibling_concrete` on named _Unparser methods in the mirror."""
import ast, sys
M='src/self-annotate/src/frontend/pure_ast.py'
mode=sys.argv[1]; names=set(sys.argv[2:])
s=open(M).read(); L=s.split('\n')
t=ast.parse(s)
c=[n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='_Unparser'][0]
ins=[]
for f in c.body:
    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name in names:
        st=min([d.lineno for d in f.decorator_list]+[f.lineno])-1
        j=st-1
        while j>=0 and (L[j].strip().startswith('#') or L[j].strip().startswith('@')):
            j-=1
        ins.append((j+1,st,f.name))
if mode=='add':
    for i,_st,n in sorted(ins, reverse=True):
        blk=[x.strip() for x in L[i:_st]]
        if '#@ sibling_concrete' in blk: print('already',n); continue
        L.insert(i,'    #@ sibling_concrete'); print('added',n)
else:
    for i,_st,n in sorted(ins, reverse=True):
        for k in range(i,_st):
            if L[k].strip()=='#@ sibling_concrete':
                del L[k]; print('removed',n); break
open(M,'w').write('\n'.join(L))
