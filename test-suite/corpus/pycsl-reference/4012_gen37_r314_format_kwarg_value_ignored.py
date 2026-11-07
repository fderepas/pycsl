r"""Test 4012 -- gen #37 route #314 (expected FAIL): `'{a}'.format(a=1) == '{a}'.format(a=2)`: the keyword value is dropped from the opaque `format_1 <hash of the receiver>` (a fresh `val` per call, so this compare FAILED at base rather than proving); REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ ensures \result == 1
def f() -> int:
    s1 = '{a}'.format(a=1)
    s2 = '{a}'.format(a=2)
    if s1 == s2:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 1, f()
