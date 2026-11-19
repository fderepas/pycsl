r"""Test 6122 -- route #417 (expected PASS): CONTROL: `list(range(n))`, `list(range(2, n))` and `for x in sorted(range(n))` with 0 <= n <= 1000 under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
def f(n: int) -> int:
    xs = list(range(n))
    zs = list(range(2, n))
    c = 0
    for x in sorted(range(n)):
        c = 1
    return 0


if __name__ == "__main__":
    print(f(10))
