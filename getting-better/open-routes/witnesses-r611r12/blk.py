# Exec the EXACT route #611 r12 block of ir_resolve.py on given module source files (CPython only).
import sys, os, textwrap
src = open(sys.argv[1]).read()
a = src.index("    if hit is not None and sys.implementation.cache_tag:")
b = src.index("    # (#49) gen #40, ROUTE #475 (red team 39;")
blk = src[a:b].replace("from errors import PyCSLSemanticError", "PyCSLSemanticError = _E")
code = ("class _E(Exception):\n    def __init__(self, m, **k):\n        super().__init__(k.get('code'), m)\n"
        "def chk(hit, parts, base, _std612, level, module_dotted, main_file):\n" + blk + "    return None\n")
ns = {"os": os, "sys": sys}
exec(compile(code, "blk", "exec"), ns)
bad = 0
for f in sys.argv[2:]:
    std = None
    if f.endswith("=std"):
        f = f[:-4]; std = os.path.dirname(f)
    try:
        ns["chk"](f, [os.path.basename(f)[:-3]], os.path.dirname(f), std, 0, "m", "main.py")
        r = "ACCEPT"
    except ns["_E"] as e:
        r = "REFUSE " + e.args[1].split("cache ")[1].split(" is one")[0]; bad += 1
    print(r, f)
print("refused", bad, "of", len(sys.argv) - 2)
