import ast, re
P='src/self-annotate/src/frontend/pure_ast.py'
OFF={'_subscript':14,'_subscript_item':13,'test_or_star_slice':12,'_call_args':12,
     'test':11,'comp_for':11,'or_test_no_cond':11,'or_test':10,'lambdef':10,
     'and_test':9,'not_test':8,'comparison':7,'expr':6,'_binop':5,'factor':4,'power':3,
     'await_expr':2,'unary_postfix':1,'trailers':0}
M=16
src=open(P).read()
lines=src.split('\n')
# 1. drop every existing GROUP VARIANT comment block (6 lines each)
out=[]
i=0
while i < len(lines):
    if lines[i].strip().startswith('# GROUP VARIANT (relaunch #11)'):
        i += 6
        continue
    out.append(lines[i]); i += 1
lines=out
tree=ast.parse('\n'.join(lines))
cls=[n for n in ast.walk(tree) if isinstance(n,ast.ClassDef) and n.name=='_Parser'][0]
targets={}
for f in cls.body:
    if isinstance(f,ast.FunctionDef) and f.name in OFF:
        targets[f.name]=f.lineno-1
assert set(targets)==set(OFF), set(OFF)-set(targets)
for name in sorted(targets, key=lambda n:-targets[n]):
    d=targets[name]
    s=d
    while s>0 and lines[s-1].lstrip().startswith('#'):
        s-=1
    block=range(s,d)
    note=[
      "    # GROUP VARIANT (relaunch #11): this method is one of the NINETEEN members of",
      "    # the expression `let rec … with …` group Why3 forms once `_binop` and",
      "    # `_subscript_item` are concrete, and all nineteen must share one well-founded",
      "    # order. Phase-offset form at multiplier 16 — the group's only provably",
      "    # cursor-advancing cycle edges leave `trailers` (the `(` before `_call_args`, the",
      f"    # `[` before `_subscript`), so every other hop is paid by a smaller offset; this",
      f"    # member sits at depth {OFF[name]}. The full depth assignment is recorded on `_binop`.",
    ]
    var=f'    #@ \\variant {M} * (\\length(self.toks) - self.i) + {OFF[name]}'
    vidx=[i for i in block if lines[i].lstrip().startswith('#@ \\variant')]
    if vidx:
        assert len(vidx)==1,(name,vidx)
        lines[vidx[0]]=var
        ins=vidx[0]
    else:
        aidx=[i for i in block if lines[i].lstrip().startswith('#@ assigns')]
        ins = aidx[0] if aidx else d
        lines.insert(ins, var)
    for k,l in enumerate(note):
        lines.insert(ins+k, l)
open(P,'w').write('\n'.join(lines))
print('rephased', len(OFF))
