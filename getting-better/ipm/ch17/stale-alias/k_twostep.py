from dataclasses import dataclass, field
from typing import Dict, List


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        self.d[1] = 5
        a = self.d
        b = a
        self.d.clear()
        return 1 if 1 in b else 0


if __name__ == "__main__":
    print(C().m())
