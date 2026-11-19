# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@dataclass
class N:
    v: int = 0


@mutable_state
@dataclass
class C:
    n: N = None

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        if self.n is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    o.n = None
    assert o.probe() == 0
