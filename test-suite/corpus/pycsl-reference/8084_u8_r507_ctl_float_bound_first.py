r"""Test 8084 -- routes #507 / #508 / #509 (control, expected PASS): `y = float(n)` under `requires -1000 <= n <= 1000` (route #417's obligation discharged) then float arithmetic with `y` and a small int literal in displays; CPython f(7, 0.25) returns 1
"""
# pycsl-expected: PASS
#@ requires -1000 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, x: float) -> int:
    y = float(n)
    v = {y, 2 * x, x * 0.5}
    w = (y * x, 1)
    return 1


if __name__ == "__main__":
    print("result", f(7, 0.25))
