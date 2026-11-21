import sys, os, json, types
sys.path.insert(0, os.path.abspath("src/pycsl"))
import pycsl as P

_orig = P.run_ir_semantic_checks
def _patched(ir_data, *a, **k):
    with open(os.environ["IRDUMP"], "w") as fh:
        json.dump(ir_data, fh, indent=1)
    return _orig(ir_data, *a, **k)
P.run_ir_semantic_checks = _patched

src = open(sys.argv[1]).read()
class A: pass
args = A()
for kk, vv in [("file", sys.argv[1]), ("allow_unverified_imports", False),
               ("strict_concurrent_checks", False), ("import_path", []),
               ("check_behavioral_subtyping", False), ("deep", False),
               ("soundness_report", False)]:
    setattr(args, kk, vv)
try:
    P._run_pipeline(src, "hoare", args)
except SystemExit:
    pass
except Exception as e:
    print("EXC:", type(e).__name__, e)
