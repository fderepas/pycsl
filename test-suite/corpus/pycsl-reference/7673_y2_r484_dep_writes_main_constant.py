r"""Test 7673 -- route #484 (expected FAIL: PROVED at base, REFUSED): a dependency does `import __main__; __main__.K = 0` at import; this file's own `K = 1` was folded; CPython returns 0.
"""
# pycsl-expected: FAIL
K = 1
import multi_file_lib.y2_h484a


#@ ensures \result == n
def f(n: int) -> int:
    return n * K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
