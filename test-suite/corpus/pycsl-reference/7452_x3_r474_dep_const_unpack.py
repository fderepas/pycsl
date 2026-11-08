r"""Test 7452 -- route #474 (expected FAIL): red-team 39 witness `g46_k1307_x_single_unpack` -- the dependency rebinds `K` by `K, = (0,)`; PROVED at base 8aaa864ca; CPython ZeroDivisionError. Now NOT PROVED.
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474c import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
