"""Test 1013 — ROUTE #32 negative witness: `len()` of a list local was
constant-folded BRANCH-INSENSITIVELY.

FALSE OF THE PROGRAM: `c == 0`, so `a = [9, 9, 9]` and Python returns 3.

At the parent commit c4233fed this printed `[+] Verification SUCCESS!`.
`_known_collection_sizes` is a FLAT, EMISSION-ORDER dict keyed only by the
local's name, so the `else` arm's literal (`[1, 2]`, size 2) overwrote the `if`
arm's (size 3) and `len(a)` folded to 2 on EVERY path. The emission is the tell:
Why3 warned `unused variable a` ONCE PER ARM and the body was the bare constant
`2` — the model had no `a` after the `if` at all, and still answered a question
about it.

`_track_collection_metadata` now POISONS both fold maps on a second binding of
the same target (a per-arm binding is indistinguishable from a rebinding from
there), so the read falls through to the real array — which, for a name bound
only inside the arms, Why3 correctly rejects as out of scope.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires c == 0
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    if c == 0:
        a = [9, 9, 9]
    else:
        a = [1, 2]
    return len(a)
