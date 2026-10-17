r"""Test 2781 — route #263 CONTROL (expected PASS): ACYCLIC method calls keep their
contract-based proof — `top -> self.mid -> self.leaf`, a `c.leaf` call from a free function,
a `super()` call to the base implementation and a same-named call on a builtin-typed field
(`self.d.get`, not `C.get`). CPython: 13.
"""
from typing import Dict

class Base:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self, k: int) -> int:
        return 1

class C(Base):
    def __init__(self) -> None:
        self.n: int = 0
        self.d: Dict[int, int] = {}

    #@ ensures \result == 3
    #@ assigns \nothing
    def leaf(self, k: int) -> int:
        return 3

    #@ ensures \result == 4
    #@ assigns \nothing
    def mid(self, k: int) -> int:
        return self.leaf(k) + 1

    #@ ensures \result == 5
    #@ assigns \nothing
    def top(self, k: int) -> int:
        return self.mid(k) + 1

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self, k: int) -> int:
        self.d.get(k)
        super().get(k)
        return 1

#@ ensures \result == 8
#@ assigns \nothing
def drive(k: int) -> int:
    c = C()
    return c.leaf(k) + c.top(k)

if __name__ == "__main__":
    c = C()
    print(drive(1) + c.top(1))
