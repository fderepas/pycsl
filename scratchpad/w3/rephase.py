import ast, re, sys
P='src/self-annotate/src/frontend/pure_ast.py'
OFF={'_call_args':12,'test':11,'comp_for':11,'or_test_no_cond':11,'or_test':10,'lambdef':10,
     'and_test':9,'not_test':8,'comparison':7,'expr':6,'_binop':5,'factor':4,'power':3,
     'await_expr':2,'unary_postfix':1,'trailers':0}
src=open(P).read()
lines=src.split('\n')
tree=ast.parse(src)
cls=[n for n in ast.walk(tree) if isinstance(n,ast.ClassDef) and n.name=='_Parser'][0]
targets={}
for f in cls.body:
    if isinstance(f,ast.FunctionDef) and f.name in OFF:
        targets[f.name]=f.lineno-1   # 0-based index of 'def' line
assert set(targets)==set(OFF), set(OFF)-set(targets)
# process from bottom to top so line indices stay valid
for name in sorted(targets, key=lambda n:-targets[n]):
    d=targets[name]
    s=d
    while s>0 and lines[s-1].lstrip().startswith('#'):
        s-=1
    block=range(s,d)
    var=f'    #@ \\variant 13 * (\\length(self.toks) - self.i) + {OFF[name]}'
    vidx=[i for i in block if lines[i].lstrip().startswith('#@ \\variant')]
    if vidx:
        assert len(vidx)==1,(name,vidx)
        lines[vidx[0]]=var
    else:
        aidx=[i for i in block if lines[i].lstrip().startswith('#@ assigns')]
        ins = aidx[0] if aidx else d
        lines.insert(ins, var)
open(P,'w').write('\n'.join(lines))
print('rephased', len(OFF))
