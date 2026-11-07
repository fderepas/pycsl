from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    n: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)

    #@ requires True
    #@ ensures \result == False
    #@ assigns \nothing
    def c(self) -> bool:
        s = set()
        s.add(2)
        self.m(s)
        return 1 in s


if __name__ == "__main__":
    print(C().c())
