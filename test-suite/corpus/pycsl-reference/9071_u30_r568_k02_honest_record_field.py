r"""Test 9071 -- u30 route #568 (expected PASS): CONTROL: a record-field claim across two calls of a method whose
frame is the record field only.
"""
# pycsl-expected: PASS
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.m(0)
    c.m(5)
    return c.a

if __name__ == "__main__":
    print(caller(C()))
