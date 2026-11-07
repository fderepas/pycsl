r"""Test 7453 -- route #474 (expected FAIL): red-team 39 witness `g46_k1315_x_try_finally` -- the dependency rebinds `K` in a `finally` arm, imported under an alias; PROVED at base 8aaa864ca; CPython ZeroDivisionError. Now NOT PROVED.
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474d import K as Z


#@ no_exception \all
def f(n: int) -> int:
    return n // Z


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
