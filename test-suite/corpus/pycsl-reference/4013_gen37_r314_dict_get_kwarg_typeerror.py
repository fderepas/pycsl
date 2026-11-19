r"""Test 4013 -- gen #37 route #314 (expected FAIL): `d.get(1, default=1)` raises TypeError in CPython; the model dropped the keyword and modelled a normal `get` (FAIL at base: the read may be None); REFUSED.
"""
# pycsl-expected: FAIL
from typing import List, Dict

#@ ensures \result == 1
def f() -> int:
    d = {1: 2}
    return d.get(1, default=1) - 1
    # TypeError

if __name__ == "__main__":
    assert f() == 1, f()
