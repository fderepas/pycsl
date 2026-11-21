r"""Test 7572 -- route #474 residual (expected FAIL: PROVED at base, NOT PROVED): a PEER module does `setattr(f2_h474, "K", 0)`; CPython returns 0.
"""
# pycsl-expected: FAIL
import multi_file_lib.f2_h474s
from multi_file_lib.f2_h474 import K


#@ ensures \result == 1
def f(n: int) -> int:
    return K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
