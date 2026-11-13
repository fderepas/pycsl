r"""Test 9895 -- W-hash x route #430 (dict-value-model-r4 §2.5, expected FAIL): an un-claimed callee hashing an UN-NARROWED `PyVal` value is admitted (ambient), and it is recorded as "may raise TypeError" for route #178's callee summary, so a `no_exception \all` caller of it is REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH). CPython raises TypeError for `caller([1], 0)`.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ ensures \result == n + 1
def h(v: PyVal, n: int) -> int:
    s = {v}
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def caller(v: PyVal, n: int) -> int:
    return h(v, n)


if __name__ == "__main__":
    try:
        print(caller([1], 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
