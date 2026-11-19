r"""Test 8680 -- route #554 (control, expected PASS): `g(k)`, `gd(k)`, `gd(k, y=k)`, `m.gd(x=k)`, `DD(k)`, `NT(a=k)`, `PC(k)`: every call binds; CPython returns 6
"""
# pycsl-expected: PASS
import multi_file_lib.u22_r554_dep as m
from multi_file_lib.u22_r554_dep import DD, NT, PC, g, gd


#@ no_exception \all
def f(k: int) -> int:
    a = DD(k)
    b = NT(a=k)
    c = PC(k)
    return g(k) + gd(k) + gd(k, y=k) + m.gd(x=k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
