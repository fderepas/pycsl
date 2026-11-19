r"""Test 7457 -- route #474 (control, expected PASS): control -- a dependency `K = 3` bound exactly once still folds: `n // K` proves `no_exception`.
"""
# pycsl-expected: PASS
from multi_file_lib.x3_h474g import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
