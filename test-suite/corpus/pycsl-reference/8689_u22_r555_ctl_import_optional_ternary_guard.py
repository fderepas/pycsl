r"""Test 8689 -- route #555 (control, expected PASS): `v = gopt(k); return v + 1 if v is not None else 0`; CPython returns 0
"""
# pycsl-expected: PASS
from multi_file_lib.u22_r555_dep import gopt


#@ no_exception \all
def f(k: int) -> int:
    v = gopt(k)
    return v + 1 if v is not None else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
