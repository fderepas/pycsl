"""Route #384 residual carrier (gen #37): an ELEMENT term in the invariant stops the
constructor goal before the list field's end state is examined, so the class is neither
given a goal nor refused, and the invariant is ASSUMED. `[0] * 4; self.disk.pop()` under
`\\length(self.disk) == 4` and `self.disk[0] == 0`: `#@ no_exception` on `self.disk[3]` PROVES,
CPython raises IndexError. Not refused because the same shape (no goal on an element term) is
route #226's residual in two mirror parsers (`Module2_Parser._ContractParser`, `pure_ast._Parser`).
"""
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
#@ class invariant self.disk[0] == 0
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * 4
        self.disk.pop()

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    try:
        D().last()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
