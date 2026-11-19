r"""Test 6016 -- gen #37 route #407 (expected FAIL): NEW latent: `K = A.copy()` of a module list `A`, then `{K}` under `no_exception \all` (CPython TypeError; PROVED at base 4431ef86f). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: a method of a container is UNKNOWN).
"""
# pycsl-expected: FAIL
A = [1]
K = A.copy()


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
