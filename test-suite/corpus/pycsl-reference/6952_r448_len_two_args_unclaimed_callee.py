r"""Test 6952 -- route #448 (expected FAIL): `len(n, n)` inside an UNCLAIMED helper `h`, called by `f` claiming `#@ no_exception \all`. PROVED on main db6c57253 (found while repairing: #441's table is consulted only under the caller's own claim); CPython raises TypeError. Now REFUSED (PYCSL-R448-BUILTIN-CROSS-CONSTRAINT: the builtin's real `inspect.signature`, in every function).
"""
# pycsl-expected: FAIL
from typing import List


def h(n: List[int]) -> int:
    return len(n, n)


#@ no_exception \all
def f(n: List[int]) -> int:
    return h(n)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
