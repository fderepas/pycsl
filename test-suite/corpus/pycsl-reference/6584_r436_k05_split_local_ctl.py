r"""Test 6584 -- route #436 (expected PASS): CONTROL (the advice of `PYCSL-R434-UNCHECKED-SITE` followed for witness 6569): the loop `for w in s.split(",", n): k += 1` written as the plain statement `k += len(s.split(",", n))` (the same count), `0 <= n <= 100` (CPython ok). (Binding `parts = s.split(",", n)` and looping over `parts` does not verify, at base either: a `for` over the opaque split value fails termination.) PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 100
#@ no_exception \all
def f(s: str, n: int) -> int:
    k = 0
    k += len(s.split(",", n))
    return k


if __name__ == "__main__":
    print("result", f("a,b", 5))
