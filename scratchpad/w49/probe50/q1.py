# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Optional


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    def pick(self, c: int) -> Optional[str]:
        if c > 0:
            return "a"
        return None

    #@ requires c < 0
    #@ ensures \result == 7
    def m(self, c: int) -> int:
        s = self.pick(c)
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1) == 0
