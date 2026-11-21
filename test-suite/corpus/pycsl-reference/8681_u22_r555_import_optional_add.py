r"""Test 8681 -- route #555 (expected FAIL: PROVED at base, REFUSED PYCSL-R555-IMPORTED-NONE-RESULT; red team 52 probe bv1215): `gnone() + 1` of an imported `def gnone() -> Optional[int]: return None`; CPython f(1) raises TypeError (NoneType + int)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r555_dep import gnone


#@ no_exception \all
def f(k: int) -> int:
    return gnone() + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
