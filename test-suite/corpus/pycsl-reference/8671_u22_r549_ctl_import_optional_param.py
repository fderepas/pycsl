r"""Test 8671 -- route #549 (control, expected PASS): `hopt(None)` of an imported `def hopt(x: Optional[int])` and `gd(k)`: the parameter admits None; CPython returns 2
"""
# pycsl-expected: PASS
from multi_file_lib.u22_r549_dep import gd, hopt


#@ no_exception \all
def f(k: int) -> int:
    return hopt(None) + gd(k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
