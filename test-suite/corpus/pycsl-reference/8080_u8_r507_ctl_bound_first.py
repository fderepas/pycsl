r"""Test 8080 -- routes #507 / #508 / #509 (control, expected PASS): the #414 / #417 operations bound to locals in plain statements under `requires 0 <= n <= 1000` (each carries its obligation), then put in set / tuple displays and `len([...])`; CPython f(5) returns 1
"""
# pycsl-expected: PASS
from typing import List


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    t = "ab" * n
    xs = [0] * n
    k = len(range(n))
    ys = list(range(n))
    v = {t}
    w = (xs, 1)
    u = len([k, len(ys)])
    return 1


if __name__ == "__main__":
    print("result", f(5))
