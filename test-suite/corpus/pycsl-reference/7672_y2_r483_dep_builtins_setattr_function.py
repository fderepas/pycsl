r"""Test 7672 -- route #483 (expected FAIL: PROVED at base, REFUSED): the dependency rebinds its own verified function `g` through `__builtins__['setattr']` on a self-import; `from y2_h483c import g` keeps `g`'s contract; CPython returns 0.
"""
# pycsl-expected: FAIL
from multi_file_lib.y2_h483c import g


#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
