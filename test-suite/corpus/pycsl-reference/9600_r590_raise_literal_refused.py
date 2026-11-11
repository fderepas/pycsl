r"""Test 9600 -- route #590 WITNESS (expected FAIL: REFUSED PYCSL-R590-RAISE-NON-EXCEPTION at HEAD, every model): `raise "boom"` raises a string. CPython raises TypeError, so the `no_exception \all` claim is false at k == 0.
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    if k == 0:
        raise "boom"
    return 1


if __name__ == "__main__":
    print(f(0))
