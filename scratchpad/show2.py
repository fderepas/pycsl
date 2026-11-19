import ast,glob,os
LIVE="src/pycsl"
targets={"_strip_all_parens":"normalize.py","_camel_to_snake":"canonical.py","_try_local_decl_kind":"stmt_control_flow.py","_body_references_bvar_0":"from_lean_json.py","_render_match_pattern":"stmt_control_flow.py","_match_pattern_cond":"expressions.py"}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    b=os.path.basename(f)
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name in targets and targets[node.name]==b:
            lines=open(f).read().splitlines()
            print("="*20, node.name, f)
            print("\n".join(lines[node.lineno-1:node.end_lineno]))
