r"""Test 2248 — route #240 (expected FAIL): in a CONTRACT `isinstance(<int>, bool)` was
`subtag tag_int tag_int`, a closed TRUE formula, so `m` discharged `g`'s precondition for the
call `g(5)` and `\result == 1` PROVED at 1e4b380e — CPython `m()` calls `g(5)` outside its
precondition and returns 0. A bool test on an int subject now takes the unknown-class arm, whose
receiver-carrying program `val` has no logic meaning: the contract is REFUSED at the WhyML
type-check (fail-closed, the same answer `requires isinstance(x, <unknown class>)` gets), never
decided.
"""
# pycsl-expected: FAIL


#@ requires isinstance(x, bool)
#@ ensures \result == 1
#@ assigns \nothing
def g(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    return g(5)
