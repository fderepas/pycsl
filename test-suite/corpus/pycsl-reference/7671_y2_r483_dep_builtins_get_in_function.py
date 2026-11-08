r"""Test 7671 -- route #483 (expected FAIL: PROVED at base, REFUSED): `__builtins__.get('exec')` inside a function the dependency calls at import rebinds the folded constant; CPython returns 0.
"""
# pycsl-expected: FAIL
from multi_file_lib.y2_h483b import K


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
