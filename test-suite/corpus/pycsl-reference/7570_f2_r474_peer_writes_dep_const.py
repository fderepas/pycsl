r"""Test 7570 -- route #474 residual (expected FAIL: PROVED at base, NOT PROVED): `from f2_h474 import K` under an ensures-only claim while the PEER module `f2_h474m` does `f2_h474.K = 0`; CPython returns 0.
"""
# pycsl-expected: FAIL
import multi_file_lib.f2_h474m
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
