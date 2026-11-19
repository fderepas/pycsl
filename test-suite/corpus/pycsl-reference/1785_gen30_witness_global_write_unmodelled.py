r"""Test 1785 — WITNESS: a write through `global` to a name that is not `#@ shared`.

Route #129. The store lands on a FRESH LOCAL while every read of the module variable is one
opaque constant, so a read before and after the write would be proved EQUAL — measured in
the refusal's own comment: `a = N; setn(); return a - N` proved 0 while Python returns -2.
Refused. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no
witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor

N = 5


#@ assigns \nothing
#@ ensures \result == 0
def setn() -> int:
    global N
    N = 3
    return 0
