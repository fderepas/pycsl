r"""Test 7472 -- route #477 (expected FAIL): red-team 39 witness `g38_q724_getattr_plus_def_shadow` -- a real `def g` next to a raising `__getattr__`; PROVED at base 8aaa864ca; CPython KeyError('__path__') at import. Now REFUSED (PYCSL-R466-IMPORTED-MODULE-RAISES).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h477c import g


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
