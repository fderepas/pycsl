"""Test 0557 — negative: arithmetic on a datatype quantifier binder is ill-typed.

`\forall c: Color; c + 1 >= 0` binds `c` over a `#@ datatype` and then applies
integer arithmetic to it. A datatype binder is not an `int`, so the lowered
`forall c : color. c + 1 >= 0` is rejected by Why3's typechecker — the typed
binder closes the false-green hole (the spec §5.3: a datatype binder may appear
only in equality and pure observers, never arithmetic).

Committed `# pycsl-expected: FAIL` and STAYS failing. (A cleaner Module-4
diagnostic for body mis-use is a documented refinement — see remains.md.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ datatype Color = Red | Green | Blue


#@ ensures \forall c: Color; c + 1 >= 0
#@ assigns \nothing
def g() -> int:
    return 0
