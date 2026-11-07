r"""Test 6607 -- route #438 (expected FAIL): red team 34 w07: `{g3(t)}` with `g3(..) -> Tuple` (un-parameterised). PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM).
"""
# pycsl-expected: FAIL
from typing import List, Tuple

def g3(t: Tuple[List[int], int]) -> Tuple:
    return t


#@ no_exception \all
def f(t: Tuple[List[int], int]) -> int:
    s = {g3(t)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1], 1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
