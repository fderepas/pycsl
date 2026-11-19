# ROUTE #158 — the `any`/`all` fold quantifies over the empty-list PLACEHOLDER's 1024 elements

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery H (with #159/#160).**
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

**Battery H (every leg predicted and hit):** emission measured BEFORE predicting (stated) — vs the
#155-#157-closed tree 1180 -> 1196, 0 MOVED / 0 GONE / 0 APPEARED, python-reference and mirrors
inert; conformance 38/38 + 38/38; suite 3679/3697 same 18, zero XPASS; planes --slow 34/34.
