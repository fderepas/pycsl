import ast,sys,glob,os
LIVE="src/pycsl"
targets={"_field_type_for":"types.py","_py_op_to_str":"Module5_IREmitter.py","_should_skip_method":"Module5_IREmitter.py","_try_local_decl_kind":"stmt_control_flow.py","_dv_store_value":"expressions.py","_is_trivial_new":"Module3_Weaver.py","_heap_var":"Module6_WhyMLTranspiler.py"}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    b=os.path.basename(f)
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name in targets and targets[node.name]==b:
            lines=open(f).read().splitlines()
            print("="*20, node.name, f)
            print("\n".join(lines[node.lineno-1:node.end_lineno]))
