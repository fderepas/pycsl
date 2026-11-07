import ast, glob
exec(open("scratchpad/idiom_scan2.py").read().split("for name in sorted")[0])

def has_none_return_guard(fn):
    for node in ast.walk(fn):
        if isinstance(node,ast.If):
            t=node.test
            isnull = (isinstance(t,ast.Compare) and len(t.ops)==1 and isinstance(t.ops[0],ast.Is) and isinstance(t.comparators[0],ast.Constant) and t.comparators[0].value is None)
            notv = (isinstance(t,ast.UnaryOp) and isinstance(t.op,ast.Not))
            if isnull or notv:
                for b in node.body:
                    if isinstance(b,ast.Return): return True
    return False
def any_tuple_unpack(fn):
    r=[]
    for node in ast.walk(fn):
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],(ast.Tuple,ast.List)):
            r.append(node.lineno)
    return r

for name in sorted(allnames):
    for f,node in funcloc.get(name,[]):
        tu=any_tuple_unpack(node)
        if tu:
            g=has_none_return_guard(node)
            print(f"{'GUARD+' if g else '      '}TUPLE {name} file={f.split('/')[-1]} L{node.lineno} unpacks@{tu}")
