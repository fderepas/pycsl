"""v42 DISAGREE — ROUTE #85. A NON-EMPTY dict literal stored to a field was modelled as the
EMPTY MAP (`{ d = (const (None: option int)) }`), so membership was DECIDED. CPython
returns 1."""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    if 1 in c.d:
        return 1
    return 0


if __name__ == "__main__":
    print(f())
