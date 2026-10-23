# OPEN ROUTE #311 — SLICE BOUNDS ARE EVALUATED RIGHT-TO-LEFT (#307 residual 4 is reachable)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witness `witnesses-r311/a05b_slice_start.py`: `zs = ys[xs[0]:inc(xs)]` emits `Array.sub ys (xs[0]) ((inc xs) - xs[0])`; Why3 evaluates
the arguments right-to-left so the start bound is read AFTER the call; pycsl proves `zs[0] == 2`, CPython gives 1.
Repair: route slice bounds (start, stop, step) through the #307 let-sequencing (receiver, start, stop, step in Python order) or refuse an
effectful bound; census every slice lowering (Array.sub, array_slice, str substring, slice assignment, del slice).
