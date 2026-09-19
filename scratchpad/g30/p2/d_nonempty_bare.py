from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
class Box:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ requires True
    #@ ensures \result == 1
    def probe(self) -> int:
        e: dict = {}
        before = 0
        if e:
            before = 1
        e["a"] = 1
        after = 0
        if e:
            after = 1
        if before == after:
            return 1
        return 2
