r"""Test 5350 -- gen #37 route #382 (expected FAIL): `d: defaultdict`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from collections import defaultdict

#@ no_exception \all
#@ ensures \result == 1
def g(d: defaultdict) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(defaultdict(int)))
