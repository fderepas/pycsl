from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ ensures \result == False
    #@ assigns self.s
    def m(self) -> bool:
        if 1 in self.s:
            return False
        a = self.s
        self.s.add(1)
        return 1 in a


if __name__ == "__main__":
    print(C().m())
