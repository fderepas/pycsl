r"""Test 8087 -- routes #507 / #508 / #509 (control, expected PASS): int / float COMPARISONS in a display (`n < x`, `n == x`: exact in CPython, no conversion, no OverflowError); CPython f(10**400, 0.5) returns 1
"""
# pycsl-expected: PASS
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, x: float) -> int:
    v = {n < x, x <= n, n == x}
    w = (n, x, 1)
    return 1


if __name__ == "__main__":
    print("result", f(10**400, 0.5))
