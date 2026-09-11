# pycsl-flags: --memory-model hoare
# ROUTE #51 shape (e) PROBE: does the LIE also poison route #44's return-annotation-gated
# `\result != None` arm?  No branch involved at all if so.
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ ensures \result != None
    #@ assigns \nothing
    def pick(self, c: int) -> str:
        if c > 0:
            return "a"
        return None


if __name__ == "__main__":
    o = C()
    assert o.pick(-1) is None
