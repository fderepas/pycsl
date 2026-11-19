r"""Test 8560 -- route #540 (control, expected PASS): `return +n` of an int under `ensures \result == n`; CPython returns n
"""
# pycsl-expected: PASS
#@ requires -1000 <= n <= 1000
#@ ensures \result == n
#@ no_exception \all
def f(n: int) -> int:
    return +n


if __name__ == "__main__":
    print("result", f(3), f(-2))
