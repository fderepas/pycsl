"""1177 — ROUTE #73, THE SPELLING THAT REFUTED THE OBVIOUS GUARD.

The natural repair — refuse when the DEFAULT argument is negative — is defeated by moving
the hazard one step: the default here is the NON-NEGATIVE literal 0 and the user's function
returns -5 regardless. CPython answers -5; `\\result >= 0` must not prove.

This driver exists so that a future narrowing of the guard to the default's sign is caught
immediately. The landed guard is STRUCTURAL instead: a bare call carries no `receiver`, and
the chained `.get(...)` the oracle legitimately serves always does.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0
#@ ensures \result == -5
#@ assigns \nothing
def get(k: str, d: int) -> int:
    return -5

#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    return get("arity", 0)
