r"""Test 5057 -- gen #37 route #373 (expected FAIL): a nested `-> List[int]` def: `t * 0 == 0` PROVED at base (CPython `[] == 0` is False). FAILS now.
"""
# pycsl-expected: FAIL
from typing import List

class P:
    #@ ensures \result == 1
    def m(self) -> int:
        def g() -> List[int]:
            return [1]
        t = g()
        return 1 if t * 0 == 0 else 0

if __name__ == "__main__":
    assert P().m() == 1, P().m()
