"""v44 DISAGREE — ROUTE #86. A `map int (option int)` PARAMETER COERCION replaced a field-read
actual with the EMPTY MAP, so the callee's contract was evaluated against a map the program
never passes. Only visible once route #85 was fixed — both erasures emitted the same wrong
constant, so one masked the other. CPython returns 1."""
from typing import Dict


#@ ensures (1 in d) ==> (\result == 1)
#@ ensures (1 not in d) ==> (\result == 0)
#@ assigns \nothing
def g(d: Dict[int, int]) -> int:
    if 1 in d:
        return 1
    return 0


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.d)


if __name__ == "__main__":
    print(f())
