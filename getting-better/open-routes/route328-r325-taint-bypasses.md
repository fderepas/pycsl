# OPEN ROUTE #328 — BYPASSES OF THE #325 TAINT CHECK: non-simple module bindings, tuple unpacking, emitter-generated binders
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r328/`: origins only collect simple top-level `Name = ..`: `A, B = 0.5, 1` (t16), `try: A = math.pi except: A = 0` (t18 — brings
back the original #322 case), `if True: A = ..` (t20), module-level `for A in [0.5]` (t17), walrus (t19), `A, *REST = [...]` (t22); inside a function
`a, b = F, 1` lowers to `let (_tu_a, _tu_b) = (f, 1)` and `_tu_a` is not tainted (t07; t11 re-opens #325's t06 via `e, _ = EPS, 0`); pattern binders
scoped to the whole declaration: `with Return r -> r` hides a global `R` (n36, n38: t06 trichotomy via `R = RATE`), `| Some v_ ->` hides a global `V_` (n33).
Repair: origins = every module/class-level binding form (all targets of Assign/AugAssign/AnnAssign/For/With/Try/Match/walrus/starred, at any
nesting); propagate taint through tuple/starred unpacking; scope binders precisely (or avoid generated binder names that can collide with
user names — coordinate with #327's injective mangling).
