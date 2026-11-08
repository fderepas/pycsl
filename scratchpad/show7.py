import ast,glob,os
LIVE="src/pycsl"
targets={"parse_expr":"parser.py","parse_implication":"parser.py","parse_disjunction":"parser.py","parse_conjunction":"parser.py","parse_arith_add":"parser.py","_heap_var":"Module6_WhyMLTranspiler.py"}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    b=os.path.basename(f)
    if b!="parser.py" and b!="Module6_WhyMLTranspiler.py": continue
    if "proof2why3" not in f and b=="parser.py": continue
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name in targets:
            lines=open(f).read().splitlines()
            print("="*20, node.name, f)
            print("\n".join(lines[node.lineno-1:node.end_lineno]))
