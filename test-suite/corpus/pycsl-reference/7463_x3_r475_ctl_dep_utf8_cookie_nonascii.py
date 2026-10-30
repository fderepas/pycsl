r"""Test 7463 -- route #475 (control, expected PASS): control -- a dependency with a `utf-8` cookie over non-ASCII text keeps verifying (`len(S) == 1`).
"""
# pycsl-expected: PASS
from multi_file_lib.x3_h475d import S


#@ ensures \result == 1
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
