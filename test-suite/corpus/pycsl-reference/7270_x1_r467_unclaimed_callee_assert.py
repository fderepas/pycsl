r"""Test 7270 -- route #467 (red team 38, expected FAIL: PROVED at base, REFUSED): an un-claimed imported `g` whose `assert x != x` fails; CPython AssertionError.
"""
# pycsl-expected: FAIL
from multi_file_lib.x1_h467a import g


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
