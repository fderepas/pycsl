r"""Test 8676 -- route #554 (expected FAIL: PROVED at base, REFUSED PYCSL-R554-IMPORTED-CALL-SIGNATURE; red team 52 probe bt1210): `PC()` of an imported class with `__init__(self, a: int)`; CPython f(1) raises TypeError (missing 1 required positional argument)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r554_dep import PC


#@ no_exception \all
def f(k: int) -> int:
    c = PC()
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
