r"""Test 7473 -- route #477 (expected FAIL): repair witness -- `import h` then a claimed function reads `h.g`, a name `h` does not bind, through its module-level `__getattr__` (which raises KeyError); PROVED at base 8aaa864ca under `#@ no_exception \all`; CPython KeyError. Now REFUSED (PYCSL-R466-IMPORTED-MODULE-RAISES, route #477).
"""
# pycsl-expected: FAIL
import multi_file_lib.x3_h477a as h


#@ no_exception \all
def f(n: int) -> int:
    if h.g:
        return n
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
