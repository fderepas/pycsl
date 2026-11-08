r"""Test 8688 -- route #555 (control, expected PASS): `gz() + 1` of an imported `-> int` returning an int module constant; CPython returns 6
"""
# pycsl-expected: PASS
from multi_file_lib.u22_r555_dep import gz


#@ no_exception \all
def f(k: int) -> int:
    return gz() + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
