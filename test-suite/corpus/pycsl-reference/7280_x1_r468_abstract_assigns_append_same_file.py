r"""Test 7280 -- route #468 (red team 38, expected FAIL: PROVED at base, REFUSED): a same-file `\abstract` `g` with `#@ assigns x` whose body appends; `len(a)` is 3 in CPython.
"""
# pycsl-expected: FAIL
from typing import List


#@ \abstract
#@ assigns x
def g(x: List[int]) -> None:
    x.append(1)


#@ requires \length(a) == 2
#@ ensures \result == 2
def f(a: List[int]) -> int:
    g(a)
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
