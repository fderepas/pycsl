from dataclasses import dataclass, field
from typing import Set

def mutable_state(cls):
    return cls

@mutable_state
@dataclass
class C:
    k: int = 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    #@ no_exception KeyError
    def m(self, s: Set[int]) -> int:
        s.remove(1)
        return 0

if __name__ == "__main__":
    try:
        C().m(set()); print("returned")
    except KeyError:
        print("KeyError")
