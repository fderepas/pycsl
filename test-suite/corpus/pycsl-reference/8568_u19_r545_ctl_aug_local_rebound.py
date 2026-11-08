r"""Test 8568 -- route #545 (control, expected PASS): `v = None; v = k; n += v` -- the None binding is overwritten before the read (#432 rebinding narrowing); CPython returns 3
"""
# pycsl-expected: PASS
#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    v = None
    v = k
    n = 0
    n += v
    return n


if __name__ == "__main__":
    print("result", f(3))
