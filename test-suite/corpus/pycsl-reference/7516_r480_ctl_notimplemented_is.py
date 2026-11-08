r"""Test 7516 -- route #480 (expected PASS): CONTROL -- `r = NotImplemented; return 0 if r is NotImplemented else 1` claiming `\result == 0` and `no_exception`. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 0
#@ no_exception \all
def f(n: int) -> int:
    r = NotImplemented
    return 0 if r is NotImplemented else 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
