from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)
    t: Set[int] = field(default_factory=set)

    #@ requires True
    #@ ensures True
    #@ assigns self.t
    def link(self) -> None:
        self.t = self.s

    #@ requires True
    #@ ensures \result == False
    #@ assigns self.s
    def m(self) -> bool:
        if 1 in self.t:
            return False
        self.s.add(1)
        return 1 in self.t


if __name__ == "__main__":
    c = C()
    c.link()
    print(c.m())
