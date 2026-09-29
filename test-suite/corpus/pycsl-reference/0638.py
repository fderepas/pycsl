"""Test 0638 — a dynamic `exec` havocs `\in_scope` (07-1839 P5a / decision C).

`exec(code)` can bind arbitrary names in the caller's scope, so afterwards `\in_scope(name)` must
NOT be decided-false for any name (the world is open). Here `requires \in_scope(ghost)` would, WITHOUT
the havoc, lower to `requires false` — vacuously satisfiable — letting the absurd `ensures \result ==
999` prove for a function that returns 0 (a soundness hole). The presence of `exec` withholds the
decided-false direction, so `\in_scope(ghost)` is unknown, the precondition is satisfiable, and the
absurd postcondition correctly FAILS. (Removing the `exec` line makes this verify — the demonstration
that the havoc is what closes the hole.)

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
# pycsl-flags: --memory-model hoare


#@ requires \in_scope(ghost)
#@ ensures \result == 999
#@ assigns \nothing
def f(code: str) -> int:
    exec(code)
    return 0
