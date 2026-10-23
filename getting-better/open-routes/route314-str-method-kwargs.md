# OPEN ROUTE #314 — KEYWORD ARGUMENTS OF str METHODS ARE DROPPED (with their effects)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r314/`: `'{a}'.format(a=inc(xs))` emits `(format_1 <hash>)` (m07); `'a b'.split(sep=str(inc(xs)))` (n07);
`'abc'.encode(errors=str(inc(xs)))` (o08). Builtins refuse keyword arguments; str methods silently drop them.
Repair: refuse keyword arguments on str (and other builtin-type) methods unless the lowering consumes them faithfully; at minimum
evaluate their effects in order (#307) before the opaque op.
