r"""Test 8682 -- route #555 (expected FAIL: PROVED at base, REFUSED PYCSL-R555-IMPORTED-NONE-RESULT; red team 52 probe cb1201): `gopt(k) * 2` of an imported `-> Optional[int]` that returns None for k > 0; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r555_dep import gopt


#@ no_exception \all
def f(k: int) -> int:
    return gopt(k) * 2


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
