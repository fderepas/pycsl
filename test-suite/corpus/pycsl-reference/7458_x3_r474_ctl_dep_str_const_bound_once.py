r"""Test 7458 -- route #474 (control, expected PASS): control -- a dependency `S = 'ab'` bound exactly once still folds: `len(S) == 2` proves.
"""
# pycsl-expected: PASS
from multi_file_lib.x3_h474g import S


#@ ensures \result == 2
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
