r"""Test 8687 -- route #555 (control, expected PASS): `v = gopt(k); if v is None: return 0; return v + 1`; CPython returns 0
"""
# pycsl-expected: PASS
from multi_file_lib.u22_r555_dep import gopt


#@ no_exception \all
def f(k: int) -> int:
    v = gopt(k)
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
