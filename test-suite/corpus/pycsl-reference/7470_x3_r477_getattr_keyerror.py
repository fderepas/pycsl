r"""Test 7470 -- route #477 (expected FAIL): red-team 39 witness `g30_b328_helper_module_getattr_raises` -- `from h import g` of a module whose PEP 562 `__getattr__` raises KeyError; PROVED at base 8aaa864ca under `#@ no_exception \all`; CPython KeyError('__path__') at import. Now REFUSED (PYCSL-R466-IMPORTED-MODULE-RAISES).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h477a import g


#@ no_exception \all
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
