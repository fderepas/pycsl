r"""Test 4014 -- gen #37 route #314 (expected FAIL): `len('a,b'.split(sep=','))`: the keyword was dropped from the opaque `split_1`; REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ ensures \result == 1
def f() -> int:
    return len('a,b'.split(sep=','))
    # CPython 2, ensures 1 should fail

if __name__ == "__main__":
    assert f() == 1, f()
