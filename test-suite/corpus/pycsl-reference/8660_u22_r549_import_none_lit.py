r"""Test 8660 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bc1332): `g(None)` of an imported `def g(x: int)`; CPython f(1) raises TypeError (in the dependency's g)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r549_dep import g


#@ no_exception \all
def f(k: int) -> int:
    return g(None)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
