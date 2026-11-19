"""Test 0639 — a dynamic `exec` is a worst-case mutator: frame-taint (07-1839 P5a').

`exec(code)` can mutate arbitrary state, so in a frame-checked model (typed/store) it WRITES the heap.
A function that runs `exec` therefore cannot honestly claim `assigns \nothing` (whose typed-model
frame condition is `ensures !int_mem = old !int_mem`): the `exec_havoc … writes {int_mem}` op makes
that postcondition unprovable, so verification correctly FAILS. (Removing the exec line makes the
empty frame hold — the demonstration that exec is what taints the frame.)

(#49) gen #33, ROUTE #229 — THIS FILE IS NOW REFUSED BEFORE IT REACHES THE DEMONSTRATION
ABOVE, AND THAT IS A REAL LOSS OF COVERAGE, recorded here rather than left to be discovered.
A bare dynamic `exec` inside a function was believed confined ("its assignments land in the
discarded locals snapshot"); a `global` declaration inside the exec'd text redirects the
assignment into the GLOBALS mapping, which at function scope is the real module globals, and
a witness PROVED `\result == 3` where CPython returns 5 (route229, corpus 1917). The text is
DYNAMIC, so the emitter cannot read it and cannot tell this file's safe `exec` from that one;
the only sound position is to refuse a non-constant `exec` wherever it stands.

So this file stays expected-FAIL and still FAILS, but by a REFUSAL rather than by the
mechanism it was written to exercise. The `\in_scope` havoc and the frame-taint machinery
still exist in the emitter and are no longer reachable from the corpus language — which
raises a question worth someone's time: IS THAT MACHINERY NOW DEAD CODE? It is recorded in
the gen #33 handoff as an open follow-up, not answered here.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed


#@ assigns \nothing
def f(code: str) -> int:
    exec(code)
    return 0
