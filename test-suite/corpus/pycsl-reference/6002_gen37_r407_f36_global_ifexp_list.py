r"""Test 6002 -- gen #37 route #407 (expected FAIL): red team 32 witness `f36_global_ifexp_list` -- an expression over a container global is taken for a hashable value (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: arithmetic / BoolOp / IfExp / slice over a container keeps the container class).
"""
# pycsl-expected: FAIL
A = [1, 2]
K = A if A else (1,)


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
