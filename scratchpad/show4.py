import ast,glob,os
LIVE="src/pycsl"
targets={"_symbol":"Module6_WhyMLTranspiler.py","_mutex_inv_application":"preamble.py","whyml_ident":"identifiers.py","_proof_reference_mlw_name":"pycsl.py","_field_type_for":"types.py"}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    b=os.path.basename(f)
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name in targets and targets[node.name]==b:
            lines=open(f).read().splitlines()
            print("="*20, node.name, f)
            print("\n".join(lines[node.lineno-1:node.end_lineno]))
