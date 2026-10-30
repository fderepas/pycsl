r"""Test 7454 -- route #474 (expected FAIL): red-team 39 witness `g49_j1703_str_const_aug` -- the dependency rebinds `S = 'a'` by `S += 'b'`; `ensures \result == 1` of `len(S)` PROVED at base 8aaa864ca; CPython returns 2. Now NOT PROVED.
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h474e import S


#@ ensures \result == 1
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
