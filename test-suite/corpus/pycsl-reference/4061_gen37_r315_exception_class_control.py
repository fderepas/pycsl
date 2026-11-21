r"""Test 4061 -- gen #37 route #315 (expected PASS): CONTROL (expected PASS): a user exception whose `__init__` is `super().__init__(msg)` + a field store is unaffected.
"""
# pycsl-expected: PASS
from typing import List, Dict
from dataclasses import dataclass, field, InitVar
from typing import NamedTuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class E(Exception):
    def __init__(self, msg: str, code: int) -> None:
        super().__init__(msg)
        self.code = code

#@ ensures \result == 7
def f() -> int:
    try:
        raise E("bad", 3)
    except E:
        return 7
    return 0

if __name__ == "__main__":
    assert f() == 7, f()
