r"""Test 6539 -- route #437 (expected FAIL): `sorted(xs)` over tuples ending in a user class without `__lt__` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R437-UNORDERED-ELEMENTS).
"""
# pycsl-expected: FAIL
from typing import List, Tuple
class C:
    def __init__(self, k: int) -> None:
        self.k: int = k


#@ no_exception \all
def f(xs: List[Tuple[int, C]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f([(1, C(1)), (1, C(2))])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
