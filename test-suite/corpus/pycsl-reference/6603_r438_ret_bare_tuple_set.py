r"""Test 6603 -- route #438 (expected FAIL): red team 34 u1: a callee `-> tuple` returning a `Tuple[List[int], int]`; the caller hashes `{g(t)}` bound to a local. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
from typing import List, Tuple

def g(t: Tuple[List[int], int]) -> tuple:
    return t


#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    k = g(t)
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1], 1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
