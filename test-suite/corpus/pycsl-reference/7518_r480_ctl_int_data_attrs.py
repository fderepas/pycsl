r"""Test 7518 -- route #480 (expected PASS): CONTROL -- `n.real + n.numerator + n.denominator` under `no_exception \all` (int's DATA attributes stay ints and are admitted). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return n.real + n.numerator + n.denominator


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
