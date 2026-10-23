# pycsl-flags: --memory-model hoare
# ROUTE #51 AT THE TUPLE TYPE: `_ghost_tuple_vars` registers a local bound to a
# tuple-returning CALL, and `<that local> is None` is decided `false`. The Module 4
# refusal landed for route #51 is scoped to `-> str`, so it does not see this.
from dataclasses import dataclass
from typing import Tuple


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    def pick(self, c: int) -> Tuple[int, int]:
        if c > 0:
            return (1, 2)
        return None

    #@ requires c < 0
    #@ ensures \result == 7
    def m(self, c: int) -> int:
        p = self.pick(c)
        if p is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1) == 0
