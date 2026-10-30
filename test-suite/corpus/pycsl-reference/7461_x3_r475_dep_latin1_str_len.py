r"""Test 7461 -- route #475 (expected FAIL): red-team 39 witness `g30_b313_dep_latin1_value` -- a `latin-1` dependency holding the bytes C3 A9 in a string (two characters for CPython, one as UTF-8); `ensures \result == 1` PROVED at base 8aaa864ca; CPython returns 2. Now REFUSED (PYCSL-R475-DEPENDENCY-ENCODING).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h475b import S


#@ ensures \result == 1
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
