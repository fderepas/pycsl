# rename.py <file> <Qualified.fn> old=new ... : rename NAME tokens within the function's line span only
import ast,io,sys,tokenize
f,q=sys.argv[1],sys.argv[2]; mp=dict(a.split("=") for a in sys.argv[3:])
src=open(f).read(); t=ast.parse(src)
def rec(n,ps):
    for c in ast.iter_child_nodes(n):
        if isinstance(c,(ast.FunctionDef,ast.ClassDef)) and c.name==ps[0]:
            if len(ps)==1: return c
            r=rec(c,ps[1:])
            if r: return r
fn=rec(t,q.split(".")); lo,hi=fn.lineno,fn.end_lineno
lines=src.split("\n"); edits=[]
for tok in tokenize.generate_tokens(io.StringIO(src).readline):
    if tok.type==tokenize.NAME and tok.string in mp and lo<=tok.start[0]<=hi:
        edits.append((tok.start,tok.end,mp[tok.string]))
n=0
for (r,c),(r2,c2),new in sorted(edits,reverse=True):
    L=lines[r-1]; lines[r-1]=L[:c]+new+L[c2:]; n+=1
# also #@ comment lines in span
open(f,"w").write("\n".join(lines)); print("renamed",n,"tokens in",q,lo,hi)
