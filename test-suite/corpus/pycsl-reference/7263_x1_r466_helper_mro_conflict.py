r"""Test 7263 -- route #466 (red team 38, expected FAIL: PROVED at base, REFUSED): the helper's `class Z(A, B)` has no consistent MRO; CPython TypeError at import.
"""
# pycsl-expected: FAIL
from multi_file_lib.x1_h466d import g


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
