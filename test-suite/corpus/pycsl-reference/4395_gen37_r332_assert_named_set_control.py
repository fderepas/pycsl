r"""Test 4395 -- gen #37 route #332 (expected PASS): CONTROL: a failing assert under the named set `no_exception IndexError` keeps the erasure: AssertionError is outside the claimed set, so the claim is true (CPython raises AssertionError, never IndexError). PROVES.
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception IndexError
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    try:
        print(g())
    except AssertionError:
        print("CPython raises AssertionError")
