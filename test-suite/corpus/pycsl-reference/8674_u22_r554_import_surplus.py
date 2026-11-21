r"""Test 8674 -- route #554 (expected FAIL: PROVED at base, REFUSED PYCSL-R554-IMPORTED-CALL-SIGNATURE; red team 52 probe bt1200): `g(k, k)` of an imported `def g(x: int)`; CPython f(1) raises TypeError (g() takes 1 positional argument but 2 were given)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r554_dep import g


#@ no_exception \all
def f(k: int) -> int:
    return g(k, k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
