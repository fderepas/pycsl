# OPEN ROUTE #326 — MODULE RESOLUTION DIFFERS FROM CPython's (shadowing stdlib modules, package vs module, sys.path) — even under --verify-imports
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 19; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r326/`: a local `math.py`/`time.py`/`os.py` next to the script is resolved by pycsl, but CPython always uses its
built-in / frozen / startup-loaded module (shadow/sh01-sh04); with both `dup19/__init__.py` and `dup19.py`, CPython loads the PACKAGE, pycsl the
.py (k04, k05); after `sys.path.insert(0, ".../alt")` CPython imports `alt/sp19.py`, pycsl the script-dir copy (k06). The wrong module itself
verifies, so --verify-imports does not help. Mechanism: `_resolve_module_path` (frontend/ir_resolve.py).
Repair: model CPython's lookup order (sys.builtin_module_names + frozen + startup-loaded stdlib names are never shadowed; package before
module) or refuse when ambiguous (a local file shadowing a stdlib/builtin module name; both pkg and module present); refuse any sys.path /
sys.modules / importlib manipulation in the verified program.
