r"""Test 8561 -- route #540 (control, expected PASS): `+(-n)` of an int (a numeric unary operand); CPython returns -n
"""
# pycsl-expected: PASS
#@ requires -1000 <= n <= 1000
#@ ensures \result == -n
#@ no_exception \all
def f(n: int) -> int:
    m = +(-n)
    return m


if __name__ == "__main__":
    print("result", f(2))
