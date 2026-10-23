from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)
    g: Dict[int, int] = field(default_factory=dict)

    #@ requires True
    #@ ensures \result == False
    #@ assigns self.d, self.g
    def m(self) -> bool:
        self.d = {}
        self.g = self.d
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    print(C().m())
