r"""Test 5352 -- gen #37 route #382 (expected FAIL): `d: Counter`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import Counter

#@ no_exception \all
#@ ensures \result == 1
def g(d: Counter) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(Counter()))
