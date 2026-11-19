r"""Test 9888 -- W-hash (dict-value-model-r4 §2.5, expected FAIL): the FALSE claim of the ambient rule: an un-claimed function whose `ensures \result == 1` holds only when hashing the `PyVal` parameter succeeds -- the TypeError is caught and turned into `return 0`. The model raises no TypeError, so the handler would be dead and the claim would prove; it is REFUSED (the handler can be reached by an exception the model does not raise, route #174 / #257). CPython: `f([1])` returns 0.
"""
# pycsl-expected: FAIL
from typing import Any

PyVal = Any


#@ ensures \result == 1
def f(v: PyVal) -> int:
    try:
        s = {v}
    except TypeError:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION: ensures \\result == 1, got", f([1]))
