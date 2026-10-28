r"""Test 6582 -- route #436 (expected PASS): CONTROL: `s.split(" ", n)` / `n + 1` with `0 <= n <= 100`, literals 1 and -1, under `no_exception \all` (CPython ok). PROVED at candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 100
#@ no_exception \all
def f(s: str, n: int) -> int:
    a = len(s.split(" ", n))
    b = len(s.split(" ", 1))
    c = len(s.split(" ", -1))
    d = len(s.split(" ", n + 1))
    return a + b + c + d


if __name__ == "__main__":
    print("result", f("a b c", 1))
