r"""Test 7678 -- route #484 (expected FAIL: PROVED at base, REFUSED): the PEER rebinds the dependency's function with `setattr(m, 'g', ...)`; CPython returns 0.
"""
# pycsl-expected: FAIL
import multi_file_lib.y2_h484r
from multi_file_lib.y2_h484g import g


#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
