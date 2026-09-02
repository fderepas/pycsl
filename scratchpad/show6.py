import ast,glob,os
LIVE="src/pycsl"
targets={"ok":"audit_proof_reverify.py","all_agree":"crosscheck.py","lean_meta_available":"extract_lean_meta.py","_is_false_goal":"pycsl.py"}
for f in glob.glob(LIVE+"/**/*.py",recursive=True):
    b=os.path.basename(f)
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name in targets and targets[node.name]==b:
            lines=open(f).read().splitlines()
            print("="*20, node.name, f)
            print("\n".join(lines[node.lineno-1:node.end_lineno]))
