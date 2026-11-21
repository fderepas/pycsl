r"""Test 8670 -- route #549 (control, expected PASS): `v: Optional[int] = None; if k > 0: v = k`, then `g(v)` under `if v is not None:`; CPython returns 2
"""
# pycsl-expected: PASS
from typing import Optional
from multi_file_lib.u22_r549_dep import g


#@ no_exception \all
def f(k: int) -> int:
    v: Optional[int] = None
    if k > 0:
        v = k
    if v is not None:
        return g(v)
    return 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
