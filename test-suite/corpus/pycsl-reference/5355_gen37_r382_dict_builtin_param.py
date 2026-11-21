r"""Test 5355 -- gen #37 route #382 (expected FAIL): `d: dict`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 1
def g(d: dict) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g({}))
