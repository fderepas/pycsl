r"""Test 6575 -- route #436 (expected FAIL): an un-claimed callee `h(s, n): return len(s.split(" ", n))` called under `no_exception \all`, n = 10**20 (CPython OverflowError): REFUSED (`PYCSL-R434-CALLEE-UNCHECKED-SITE`). PROVED at base 78b519f63.
"""
# pycsl-expected: FAIL
def h(s: str, n: int) -> int:
    return len(s.split(" ", n))


#@ no_exception \all
def f(s: str, n: int) -> int:
    return h(s, n)


if __name__ == "__main__":
    try:
        print("result", f("a b", 10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
