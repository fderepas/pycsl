from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ assigns o.d
    def link_to(self, o: "C") -> None:
        o.d = self.d

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        o = C()
        self.d[1] = 5
        self.link_to(o)
        self.d.clear()
        return 1 if 1 in o.d else 0


if __name__ == "__main__":
    print(C().m())
