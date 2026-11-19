r"""Test 6960 -- route #449 (expected FAIL): the mismatch `g(n, n)` sits in an UNCLAIMED helper `h`; `f` claims `#@ no_exception \all` and calls `h`. PROVED on main db6c57253 (found while repairing: the caller's claim covers what the callee raises, so the check runs in every function); CPython raises TypeError. Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
def g(a: int) -> int:
    return a


def h(n: int) -> int:
    return g(n, n)


#@ no_exception \all
def f(n: int) -> int:
    return h(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
