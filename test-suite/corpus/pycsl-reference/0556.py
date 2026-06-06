"""Test 0556 — negative: an unresolved quantifier binder type is rejected.

`\forall x: Bogus; …` names a binder type `Bogus` that is neither a scalar nor a
declared `#@ datatype` / class. Under quantification.md P1 this is a HARD Module 4
error (`_validate_quant_binders`) — the spec §5.1 soundness rule: a typed binder is
NEVER silently defaulted to `int`. Negative twin of the flagship 0555.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \forall x: Bogus; x == x
#@ assigns \nothing
def f() -> int:
    return 0
