r"""Test 8566 -- route #545 (control, expected PASS): `-one(k)` of a `-> int` def under `ensures \result == -(k + 1)`; CPython returns -4
"""
# pycsl-expected: PASS
#@ requires 0 <= k <= 1000
#@ ensures \result == k + 1
#@ no_exception \all
def one(k: int) -> int:
    return k + 1


#@ requires 0 <= k <= 1000
#@ ensures \result == -(k + 1)
#@ no_exception \all
def f(k: int) -> int:
    return -one(k)


if __name__ == "__main__":
    print("result", f(3))
