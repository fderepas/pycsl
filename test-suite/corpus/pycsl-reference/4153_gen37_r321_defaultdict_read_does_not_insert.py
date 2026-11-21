r"""Test 4153 -- gen #37 route #321 (expected FAIL): `x = d[5]; 5 in d` decided False: CPython's defaultdict read INSERTS the key. An unfused read with an observation is REFUSED.
"""
# pycsl-expected: FAIL
from collections import defaultdict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = defaultdict(int)
    x = d[5]
    if 5 in d:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
