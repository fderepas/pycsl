r"""Test 8679 -- route #554 (expected FAIL: PROVED at base, REFUSED PYCSL-R554-IMPORTED-CALL-SIGNATURE; red team 52 probe cc1218): `m.gd(k, k, k)` of an imported `def gd(x: int, y: int = 0)`; CPython f(1) raises TypeError (takes from 1 to 2 positional arguments but 3 were given)
"""
# pycsl-expected: FAIL
import multi_file_lib.u22_r554_dep as m


#@ no_exception \all
def f(k: int) -> int:
    return m.gd(k, k, k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
