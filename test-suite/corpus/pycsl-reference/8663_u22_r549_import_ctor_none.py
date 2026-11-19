r"""Test 8663 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bn1218): `DC(None)` of an imported class with `__init__(self, x: int)`; CPython f(1) raises TypeError (in DC.__init__)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r549_dep import DC


#@ no_exception \all
def f(k: int) -> int:
    c = DC(None)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
