r"""Test 5351 -- gen #37 route #382 (expected FAIL): `d: array.array`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
import array

#@ no_exception \all
#@ ensures \result == 1
def g(d: array.array) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(array.array('i')))
