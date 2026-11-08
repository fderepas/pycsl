r"""Test 6120 -- route #417 (expected PASS): CONTROL: `[7] * n` (0 <= n <= 100) has length n and `[7] * 3` has `xs[2] == 7` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 100
#@ ensures \result == n
#@ no_exception \all
def f(n: int) -> int:
    xs = [7] * n
    return len(xs)


#@ ensures \result == 7
#@ no_exception \all
def g() -> int:
    xs = [7] * 3
    return xs[2]


if __name__ == "__main__":
    print(f(5), g())
