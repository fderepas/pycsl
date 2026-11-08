r"""Test 8669 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bn1215): `g(v := None)` of an imported `def g(x: int)`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r549_dep import g


#@ no_exception \all
def f(k: int) -> int:
    return g(v := None)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
