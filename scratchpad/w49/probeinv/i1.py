# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


#@ class invariant self.x >= 0
@mutable_state
@dataclass
class C:
    x: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns self.x
    def bad(self) -> None:
        self.x = -1


if __name__ == "__main__":
    o = C()
    o.bad()
    assert o.x == -1
