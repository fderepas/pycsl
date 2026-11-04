r"""Test 8684 -- route #555 (expected FAIL: PROVED at base, REFUSED PYCSL-R555-IMPORTED-NONE-RESULT; red team 52 probe cb1210): `gpipe(k) < 3` of an imported `-> int | None`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r555_dep import gpipe


#@ no_exception \all
def f(k: int) -> int:
    return 1 if gpipe(k) < 3 else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
