r"""Test 6123 -- route #417 (expected PASS): CONTROL: `float(n)` with -1000 <= n <= 1000 and `float(len("abc"))` under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires -1000 <= n and n <= 1000
#@ no_exception \all
def f(n: int) -> int:
    x = float(n)
    y = float(len("abc"))
    return 0


if __name__ == "__main__":
    print(f(10))
