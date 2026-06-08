"""Test 0638 — a dynamic `exec` havocs `\in_scope` (07-1839 P5a / decision C).

`exec(code)` can bind arbitrary names in the caller's scope, so afterwards `\in_scope(name)` must
NOT be decided-false for any name (the world is open). Here `requires \in_scope(ghost)` would, WITHOUT
the havoc, lower to `requires false` — vacuously satisfiable — letting the absurd `ensures \result ==
999` prove for a function that returns 0 (a soundness hole). The presence of `exec` withholds the
decided-false direction, so `\in_scope(ghost)` is unknown, the precondition is satisfiable, and the
absurd postcondition correctly FAILS. (Removing the `exec` line makes this verify — the demonstration
that the havoc is what closes the hole.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


#@ requires \in_scope(ghost)
#@ ensures \result == 999
#@ assigns \nothing
def f(code: str) -> int:
    exec(code)
    return 0
