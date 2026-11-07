r"""Test 7506 -- route #480 (expected FAIL): `n.bit_length + 1` -- an UNCALLED method of an int parameter. PROVED at base; CPython TypeError; now REFUSED (R325: of int's attributes only real / imag / numerator / denominator are ints).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return n.bit_length + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
