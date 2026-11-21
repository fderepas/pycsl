import ast,sys
LIVE="src/pycsl"
def show(rel,name):
    import os
    s=open(os.path.join(LIVE,rel)).read()
    for node in ast.walk(ast.parse(s)):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            print("### %s::%s"%(rel,name)); print(ast.get_source_segment(s,node)); print()
            return
    print("NOTFOUND",rel,name)
for a in sys.argv[1:]:
    rel,name=a.split("::"); show(rel,name)
