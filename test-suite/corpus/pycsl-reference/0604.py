"""Test 0604 — string `in` in a contract is a well-formed logic term (07-0647-spec S2.1/R10).

`requires n in h` for strings must lower to a `string.String` logic formula (substring
containment), not an array `exists … Array.length …` (wrong theory, `Array.length` unbound) nor a
program `val` (illegal in a formula — "unbound symbol"). RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires n in h
#@ ensures \result == 1
#@ assigns \nothing
def f(h: str, n: str) -> int:
    return 1
