# OPEN ROUTE #288 — ELEMENT STORE THROUGH A LIST RETURNED BY A CALL IS NOT SEEN AS ALIASING
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r288/`. a009/a010/a013: `b = ident2(a); b[0] = 5; return a[0]` proves `== 1` (CPython 5) when the callee is imported (a `val` with a fresh result; also under --verify-imports); a012 same-file \trusted callee; a015/a020/a017/a021 same-file VERIFIED callee with an early return (Return_seq snapshot -> copy). #283 refuses mutator methods / augmented assignment on such aliases but not subscript stores. Repair: element stores (and every write) through a list bound from a call that may return (an alias of) a parameter are refused unless the callee provably returns a fresh list; an imported/trusted callee is "may alias" by default.

## REPAIR (2026-10-20, worktree pycsl-rB off 7313506b)
Root cause (located on the emission of each witness): `b = ident2(a)` lowers to `let b = (ident2 a) in
b[0] <- 5`, and the callee's result is a region DISTINCT from `a` for Why3 whenever the callee is a `val` —
imported (also under `--verify-imports`: the caller still sees the interface `val`), `\trusted`, or a
verified body whose `return` goes through `raise (Return_seq (snapshot x))` (an early return, a return in a
loop: a COPY). #283's partner rule (B) ran only for a SEQ-PROMOTED target and its mutation set was #279's
(mutator methods, augmented assignment; element stores only for a chained temporary), so an element store —
or a store through the partner — was never seen.

Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; base = 7313506b; census
probes under `scratchpad/rB/p288`):

| shape | base | after |
|---|---|---|
| imported `b: List[int] = ident2(a); b[0] = 5; return a[0]` (a009 / 3370) | PROVED | REFUSED |
| same under `--verify-imports` (a010 / 3371) | PROVED | REFUSED |
| same-file `\trusted` callee (a012 / 3372) | PROVED | REFUSED |
| imported, on a PARAMETER, `\result == \old(a[0])` (a013 / 3373) | PROVED | REFUSED |
| verified callee with an early return (a015 / 3374), `b[0] += 4` (a017 / 3375) | PROVED | REFUSED |
| REVERSE: `b = pick(a, c); a[0] = 5; return b[0]` (a020 / 3376); imported reverse | PROVED | REFUSED |
| return from inside a loop, unannotated `b` (a021 / 3377) | PROVED | REFUSED |
| slice store `b[0:1] = [9]` (3378), store in a loop (3379), store in an `if`, `b = tid(tid(a))` (3381), `c = b; c[0] = 5`, `b[1] *= 3`, `b = pick(a, c)` unannotated | PROVED (emitted; slice/loop/nested proved) | REFUSED |
| the alias handed to a WRITING callee `setfirst(b)` (`assigns x[0]`) (3380); imported writer `push(b)` | PROVED (emitted) | REFUSED |
| `del b[0]` | REFUSED (list `del`) | REFUSED (this rule first) |
| `b = a if c > 0 else [9, 9]; b[0] = 5`, `b = a or [9, 9]; b[0] = 5` | FAIL (no-effect `subscript_set`, ill-typed) | REFUSED (#289's gate) |
| controls 3382: FRESH-returning callee with list-free arguments stored through; read-only returned alias | PASS | PASS |
| `b = tid(a); a[1] = 6; return a[1]` (alias never used again) | PASS | REFUSED (coarse, see residuals) |

Rule (inline in `_handle_assign_stmt`, #283's block; mirror twin `\trusted` and already declaring `#@ raises`;
no new def/field; #283's message and code `PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS` reused, so its census
rows stand): (i) the PARTNER set is collected for ANY list-valued target — seq-promoted, symbol-table `list`,
or an RHS that `_rhs_yields_array` (an unannotated call returning a list) — instead of only a seq-promoted one;
an index READ of a 1-D list (`make(a[0])`) contributes only its index (a scalar is not the list); (ii) with a
partner set, the flow-sensitive #279 walk now also refuses an ELEMENT STORE, a SLICE STORE and `del` through
any live name (target or partner), and a live name passed as a direct argument to a user/imported function
whose declared `assigns` is not exactly `\nothing` (name-keyed on the last component; a collision only refuses
more; library callees remain #162's). An imported/trusted callee is "may alias" by construction: no freshness
analysis (measured population of the coarse cut: 0, see blast radius).
Census (the family): every store/write form through a call-bound list was probed — element store, augmented
element store, slice store, `del`, store in a loop / `if`, nested call, two-step name alias, reverse-direction
store, writing callee (same-file and imported), conditional / `or` selection (#289's gate) — each REFUSED.
Mutator methods / `+=` on the alias were already #283 (B)/#279. Dict/set aliases bound from a call: the store
lowers through `map_update` on a COPY too, but every probe (`e = idd(d); e[1] = 2`) is ill-typed (fail-closed)
before and after — residual, not reached by this rule.
