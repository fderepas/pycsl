r"""Test 7451 -- route #474 (expected FAIL): red-team 39 witness `g42_c962_if_rebind` -- the dependency rebinds `K` inside an `if` arm; PROVED at base 8aaa864ca; CPython ZeroDivisionError. Now NOT PROVED.
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474b import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
