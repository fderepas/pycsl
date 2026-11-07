from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ requires t == "x"
    #@ ensures \result == 7
    def m(self, c: int, t: str) -> int:
        s = t
        s = None
        if c > 0:
            s = t
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1, "x") == 0
