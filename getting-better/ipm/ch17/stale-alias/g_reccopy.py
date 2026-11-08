from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ assigns self.d
    def put(self) -> None:
        self.d[1] = 5

    #@ assigns self.d
    def reset(self) -> None:
        self.d.clear()

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        self.put()
        c2 = self
        self.reset()
        return 1 if 1 in c2.d else 0


if __name__ == "__main__":
    print(C().m())
