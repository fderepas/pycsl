"""Test 1198 — ROUTE #78: a SEEDED `deque(...)` is REFUSED.

`Module5_IREmitter._py_expr_call`'s `deque` arm reduces a deque to the list/array model by
returning an EMPTY `ArrayLit` — DISCARDING EVERY ARGUMENT — under a comment that called it
"a sound under-approximation". **It is not one.** An empty array is not a weaker fact about
a three-element one; it is a DIFFERENT CONCRETE VALUE, and the emitter then proves definite
facts from it. A real under-approximation would be an UNCONSTRAINED value. Measured, before
this refusal:

    dq = deque([1, 2, 3])
    return len(dq)
    #@ ensures \\result == 0          <-- FALSE OF THE PROGRAM (Python returns 3)

    [+] Verification SUCCESS! All contracts formally proven.

BOTH DIRECTIONS WERE MEASURED: the TRUE twin (`\\result == 3`) was REFUSED while the false
one PROVED, which is what makes it a route and not a gap. The element read `dq[0]` is a
second carrier (proved 0 where Python gives 5), and the stale length also DISCHARGED A
CALLEE'S `requires` at a call site, so the defect propagated across the call graph.

HOW IT WAS FOUND: by the generator route #77 produced — *a prose carve-out in the module
upstream of a guard is an unexploited route with a signpost on it.* A census of comments
admitting a construct is unmodelled/dropped/"a sound under-approximation" turned this up
directly, along with routes #79 and #80.

WHAT BOUNDS THE REFUSAL: the EMPTY form is FAITHFUL and keeps working — `deque()` really is
`[]`. Corpus 0501 relies on it and still proves, and 1199 is the dedicated control. Census:
`deque()` at 0501 is the ONLY use in either verified corpus, and the self-annotation mirror
contains no `deque(` at all, so this guard is byte-inert BY CONSTRUCTION.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from collections import deque


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    dq = deque([1, 2, 3])
    return len(dq)
