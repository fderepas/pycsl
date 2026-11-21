from dataclasses import dataclass, field
from typing import Set

def mutable_state(cls):
    return cls

@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ ensures \result == 0
    #@ assigns self.s
    #@ no_exception KeyError
    def m(self) -> int:
        self.s.remove(1)
        return 0

if __name__ == "__main__":
    try:
        C().m(); print("returned")
    except KeyError:
        print("KeyError")
