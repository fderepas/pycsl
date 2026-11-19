r"""Test 6577 -- route #436 (expected FAIL): `s.split(" ", g(n))` (a call as maxsplit) under `no_exception \all`, n = 10**20 (CPython OverflowError): REFUSED (`PYCSL-R436-SSIZE-ARGUMENT`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.split(" ", g(n)))


if __name__ == "__main__":
    try:
        print("result", f("a b", 10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
