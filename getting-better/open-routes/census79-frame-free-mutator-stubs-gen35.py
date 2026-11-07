import ast, os, re, sys, collections
emit=sys.argv[1]
# live classes: name -> {method: mutates_self(bool)}
live={}
for dp,dn,fns in os.walk('src/pycsl'):
    for fn in fns:
        if not fn.endswith('.py'): continue
        try: t=ast.parse(open(os.path.join(dp,fn)).read())
        except Exception: continue
        for c in ast.walk(t):
            if isinstance(c,ast.ClassDef):
                d=live.setdefault(c.name.lower(),{})
                for f in c.body:
                    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        mut=False
                        for n in ast.walk(f):
                            tg=[]
                            if isinstance(n,(ast.Assign)): tg=n.targets
                            elif isinstance(n,(ast.AugAssign,ast.AnnAssign)): tg=[n.target]
                            for x in tg:
                                b=x
                                while isinstance(b,(ast.Subscript,ast.Attribute)) and not (isinstance(b,ast.Attribute) and isinstance(b.value,ast.Name) and b.value.id=='self'):
                                    b=b.value
                                if isinstance(b,ast.Attribute) and isinstance(b.value,ast.Name) and b.value.id=='self': mut=True
                            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('append','extend','add','update','pop','remove','discard','clear','insert','setdefault') :
                                b=n.func.value
                                while isinstance(b,(ast.Subscript,ast.Attribute)) and not (isinstance(b,ast.Attribute) and isinstance(b.value,ast.Name) and b.value.id=='self'):
                                    b=b.value
                                if isinstance(b,ast.Attribute) and isinstance(b.value,ast.Name) and b.value.id=='self': mut=True
                        d[f.name]=d.get(f.name,False) or mut
tot=collections.Counter(); rows=[]
for f in sorted(os.listdir(emit)):
    if not f.endswith('.mlw'): continue
    txt=open(os.path.join(emit,f)).read()
    for m in re.finditer(r'^  val (\w+?)__(\w+) \(self: (\w+)\)[^\n]*\n((?:    [^\n]*\n)*)',txt,re.M):
        cls,meth,rt,blk=m.group(1),m.group(2),m.group(3),m.group(4)
        if 'writes' in blk: continue
        if cls not in live or meth not in live[cls]: continue
        if not live[cls][meth]: continue
        # call sites: the full name or an abstract op ending _<meth>_<n>
        full=len(re.findall(r'\b%s__%s\b'%(cls,re.escape(meth)),txt))-1
        ops=len(re.findall(r'\b\w+_%s_\d+\b'%re.escape(meth.lstrip('_')),txt))
        rec = bool(re.search(r'type %s = \{'%cls, txt))
        tot['frame-free-mutator-vals']+=1
        if full>0 or ops>0: tot['with-call-sites']+=1; rows.append((f,cls,meth,full,ops,rec))
print(dict(tot))
for r in rows[:60]: print(*r)
