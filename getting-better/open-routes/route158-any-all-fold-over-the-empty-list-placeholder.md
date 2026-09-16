# ROUTE #158 — the `any`/`all` fold quantifies over the empty-list PLACEHOLDER's 1024 elements

**Status: REPAIR DRAFTED by gen #29 (worktree wtI, on top of battery G's candidate); battery H pending.**
Severity 1. Generator: hand (comprehension batch).

## Measured at `e27e6797`

    all(x > 0 for x in [])          #@ ensures \result != 1   PROVED (CPython 1)
    any(x == 0 for x in [])         #@ ensures \result != 0   PROVED (CPython 0)
    xs = []; all(x > 0 for x in xs) #@ ensures \result != 1   PROVED (CPython 1)

`_try_emit_any_all_fold` emits an iff-specified fold over `Array.length a`; an empty list literal
lowers to the emitter's placeholder `(Array.make 1024 0)` (lesson (ao)), so the fold answers for
1024 zeros. `len`, `sum`, `for`, `in` and truthiness over `[]` use the known size and are fail-closed.

## Repair

The fold declines (the unconstrained oracle stays) when the iterable is the placeholder literal, or
an identifier that is an append target, a rebound collection, or known to have size 0.
`_try_emit_any_all_fold` is unmirrored. Witnesses 1534-1536 (XFAIL), 1537 (PASS control).
