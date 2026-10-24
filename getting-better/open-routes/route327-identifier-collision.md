# OPEN ROUTE #327 — TWO PYTHON NAMES LOWER TO ONE WhyML IDENTIFIER (whyml_ident case-fold / reserved-word prefix, no collision check)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r327/`: `whyml_ident` lowercases a leading capital (N, n -> n) and prefixes reserved words (result -> py_result) with no
collision check: `N = len(xs); n = 0; return N == n` proves True (n40; emitted three `let n = ref ..` then `!n = !n`), n24, n09; reserved-word
prefix vs an existing `py_result`/`py_model` (n27, n14); global `K = mk()` vs param `k` -> `return K` returns the parameter (n31); `F = 0.5` vs a
param `f` also bypasses #325 (n06). Inlined int constants are safe. Needs no float — miscompiles plain int code.
Repair: make identifier mangling INJECTIVE per scope (e.g. encode case: `N` -> `n'U`/`_N` style, reserved-word prefix that cannot collide,
uniqueness check with a deterministic suffix), or refuse a program where two distinct source names (incl. globals vs locals/params,
generated names like _tu_*, py_*, v_, r) map to the same WhyML identifier in one scope. Census all identifier-mangling sites.
