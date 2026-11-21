r"""Test 7675 -- route #484 (expected FAIL: PROVED at base, REFUSED): a package `__init__` on the dotted path writes `__main__.K = 0`; CPython returns 0.
"""
# pycsl-expected: FAIL
K = 1
import multi_file_lib.y2_p484.sub


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
