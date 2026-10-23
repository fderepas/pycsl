# OPEN ROUTE #319 — A LIST PARAMETER REBOUND INSIDE A NESTED BLOCK IS LOST AFTER THE BLOCK (block-scoped `let`), LATER WRITES HIT THE CALLER
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r319/`: `if b: xs = [7,7,7]` then `len(xs)` proves 2 (CPython 3) (p01); same in `for` (l25), element read (p03), nested if
(p08); `if b: xs = [7,7]; xs[0] = 9` proves `ensures xs[0] == 9` with `assigns xs[0]` while the CALLER's list is untouched in CPython (p14 — the
caller-visible frame is wrong). Mechanism: inside if/for/while, `xs = [...]` lowers to a block-scoped `let xs = (Array.make ...) in`; after
the block `xs` denotes the parameter again. Top-level, try and match rebinds use `ref xs` (correct or ill-typed).
Repair: a parameter (or any local) rebound anywhere in the body must be a `ref` for the whole body (or the rebind refused when it occurs
inside a nested block); writes after a rebind must target the new object, never the caller's.
