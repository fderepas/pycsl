r"""Test 8082 -- routes #507 / #508 / #509 (control, expected PASS): int * int, float * float / + / - inside displays (no conversion: int arithmetic is exact, float overflow gives inf); CPython f(10**400, 10**400, 0.5, 1e300) returns 1
"""
# pycsl-expected: PASS
#@ no_exception \all
#@ ensures \result == 1
def f(a: int, b: int, x: float, y: float) -> int:
    v = {a * b}
    w = (x * y, x + y, 1)
    u = len([a - b, x - y])
    return 1


if __name__ == "__main__":
    print("result", f(10**400, 10**400, 0.5, 1e300))
