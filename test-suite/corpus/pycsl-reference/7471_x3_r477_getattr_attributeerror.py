r"""Test 7471 -- route #477 (expected FAIL): red-team 39 witness `g38_q721_getattr_raises_attr_for_g` -- the module `__getattr__` raises AttributeError for `g`; PROVED at base 8aaa864ca; CPython ImportError. Now REFUSED (PYCSL-R466-IMPORTED-MODULE-RAISES).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h477b import g


#@ no_exception \all
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
