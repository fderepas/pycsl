r"""Test 7571 -- route #474 residual (expected FAIL: PROVED at base, NOT PROVED): `from f2_p474.sub import K` while the package `__init__` does `from . import sub; sub.K = 0`; CPython returns 0.
"""
# pycsl-expected: FAIL
from multi_file_lib.f2_p474.sub import K


#@ ensures \result == 1
def f(n: int) -> int:
    return K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
