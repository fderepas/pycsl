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
        d = self.d
        before = 0
        if d:
            before = 1
        d["a"] = 1
        after = 0
        if d:
            after = 1
        if before == after:
            return 1
        return 2
