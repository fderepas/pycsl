r"""Test 5354 -- gen #37 route #382 (expected FAIL): `d: list`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 1
def g(d: list) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g([]))
