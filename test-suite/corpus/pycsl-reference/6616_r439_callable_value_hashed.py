r"""Test 6616 -- route #439 (expected FAIL): red team 34 pp11: `{c}` with `c: Callable[[], int]`, called with an instance of a class with `__call__` and `__hash__ = None`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import Callable

class Cc:
    __hash__ = None

    def __call__(self) -> int:
        return 1


#@ no_exception \all
def f(c: Callable[[], int]) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(Cc())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
