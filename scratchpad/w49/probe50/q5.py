# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    name: str = ""

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        if self.name is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    o.name = None
    assert o.probe() == 0
