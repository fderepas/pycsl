r"""Test 7455 -- route #474 (expected FAIL): family witness -- the dependency rebinds `K` through `globals()["K"] = 0`, a namespace writer the binding-site table cannot see; CPython ZeroDivisionError. REFUSED at base 8aaa864ca and now by the dependency's own Weaver namespace-write guard; route #474's allow-list also declines the fold from a module with a namespace writer (belt and braces).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474f import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
