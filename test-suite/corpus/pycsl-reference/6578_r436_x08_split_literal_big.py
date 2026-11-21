r"""Test 6578 -- route #436 (expected FAIL): `s.split(" ", 100000000000000000000)` under `no_exception \all` (CPython OverflowError): REFUSED at emission (`PYCSL-R436-SSIZE-ARGUMENT`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(s: str) -> int:
    return len(s.split(" ", 100000000000000000000))


if __name__ == "__main__":
    try:
        print("result", f("a b"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
