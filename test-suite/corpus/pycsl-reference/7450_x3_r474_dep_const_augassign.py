r"""Test 7450 -- route #474 (expected FAIL): red-team 39 witness `g46_k1304_x_sub_aug` -- the dependency rebinds `K = 1` by `K -= 1`; the importer folded `K` to 1 and `n // K` PROVED at base 8aaa864ca under `#@ no_exception \all`; CPython ZeroDivisionError. Now NOT PROVED (the fold is dropped).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474a import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
