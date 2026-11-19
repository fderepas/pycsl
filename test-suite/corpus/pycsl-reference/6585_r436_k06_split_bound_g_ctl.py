r"""Test 6585 -- route #436 (expected PASS): CONTROL (the advice of `PYCSL-R436-SSIZE-ARGUMENT` followed for witness 6577): `m = g(n)` bound first, then `s.split(" ", m)`, `0 <= n <= 100` (CPython ok). PROVED at candidate.
"""
# pycsl-expected: PASS
#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ requires 0 <= n and n <= 100
#@ no_exception \all
def f(s: str, n: int) -> int:
    m = g(n)
    return len(s.split(" ", m))


if __name__ == "__main__":
    print("result", f("a b", 1))
