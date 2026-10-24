# OPEN ROUTE #338 — OVERRIDE RETURN TYPES NOT COMPARED (`-> int` overridden `-> float`), and FIELD STORES FROM OUTSIDE THE CLASS HIERARCHY NOT COUNTED BY #334
**Status: OPEN (gen #37, 2026-10-24), Severity 2.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates).
Witnesses `witnesses-r338/`: F4_residuals.py (3): #334 residuals 6 and 1 (overridden `-> int` method returning float used as initialiser;
unannotated-param initialiser) + new g_call_override: base `-> int` overridden `-> float` called as `b.m()` on a base-typed parameter — the refinement
goal is `true -> true`, return types never compared (mypy rejects, CPython runs). F5_external_store.py (2): a float stored into an unannotated
int-inferred field from `__main__`/module code (`c.r = 0.5`, setattr) is not among #334's stores (class/bases/descendants only).
Repair: the #277 override refinement must compare return (and parameter) types — refuse an override whose return annotation is not a subtype;
#334's store census must include stores from module-level code and any function (or refuse external field stores of non-int values).
