r"""Test 6118 -- route #417 (expected PASS): CONTROL: textually identical `sorted(range(n))` / `list(range(n))` / `float(n)` calls, every obligation kept, with 0 <= n <= 100 under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 100
#@ no_exception \all
def f(n: int) -> int:
    c = 0
    for x in sorted(range(n)):
        c = 1
    for y in sorted(range(n)):
        c = 2
    xs = list(range(n))
    ys = list(range(n))
    a = float(n)
    b = float(n)
    return 0


if __name__ == "__main__":
    print(f(5))
