r"""Test 7268 -- route #466 (red team 38, expected FAIL: PROVED at base, REFUSED): the helper's own import raises (a dependency of a dependency); CPython ZeroDivisionError.
"""
# pycsl-expected: FAIL
from multi_file_lib.x1_h466h import g


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
