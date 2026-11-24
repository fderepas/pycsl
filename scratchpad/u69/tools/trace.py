# trace.py <tree> <code-substring> <pycsl args...> : run pycsl.py, printing the Python stack where a
# PyCSLSemanticError whose code contains <code-substring> is constructed
import sys, os, runpy, traceback
T, CODE = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(T, "src", "pycsl"))
import errors
_orig = errors.PyCSLSemanticError.__init__
def _init(self, *a, **k):
    if CODE in str(k.get("code", "")):
        print("=== TRACE", k.get("code"), k.get("filename"), file=sys.stderr)
        traceback.print_stack(limit=8, file=sys.stderr)
    _orig(self, *a, **k)
errors.PyCSLSemanticError.__init__ = _init
sys.argv = [os.path.join(T, "src", "pycsl", "pycsl.py")] + sys.argv[3:]
runpy.run_path(sys.argv[0], run_name="__main__")
