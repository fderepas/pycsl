r"""Test 9068 -- u30 route #568 (expected FAIL): CONTROL (unchanged): the same false claim through `self.m(..)` in
a no-record class, whose stub already carried `writes { _pyobj_state }`: NOT PROVED at the base and at HEAD.
"""
# pycsl-expected: FAIL
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ assigns self.flag
    def __init__(self) -> None:
        pass

    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

    #@ ensures \result == 1
    #@ assigns self.flag
    def caller(self, o: Any) -> int:
        self.m(0)
        x = getattr(o, "flag", 0)
        self.m(5)
        y = getattr(o, "flag", 0)
        if x or not y:
            return 1
        return 2

if __name__ == "__main__":
    k = C()
    print(k.caller(k))
