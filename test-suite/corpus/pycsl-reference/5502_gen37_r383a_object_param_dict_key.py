r"""Test 5502 -- gen #37 route #383 allow-list addendum (expected FAIL): `d: object` as a dict key `{d: 1}`, called with a dict (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 1
def g(d: object) -> int:
    m = {d: 1}
    return 1

if __name__ == "__main__":
    print(g({}))
