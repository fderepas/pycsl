# OPEN ROUTE #320 — REBINDING A LOCAL LIST TO A LIST LITERAL OVERWRITES THE SAME ARRAY IN PLACE (aliases see the new contents)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r320/`: `ys = xs; xs = [7, 8]; return ys[0]` proves 7 (CPython 1) (p10); same with the rebind inside an if (p17);
`for x in xs: t += x; xs = [100]*4-literal` — the loop reads the overwritten elements, `\result != 10` proves (CPython 10) (l49).
Mechanism: `xs = [7, 8]` on an existing local list emits `xs_len := 0; xs[!xs_len] <- 7; ...` into the existing `Array.make` instead of a
fresh array. #279 refuses only a MUTATED alias; a non-literal RHS is refused; the literal path is the hole.
Repair: a literal rebind of a local list must allocate a fresh array (ref rebinding) or be refused when the local may be aliased
(any prior `ys = xs`, iteration in progress, passed to a callee, stored in a container/field).
