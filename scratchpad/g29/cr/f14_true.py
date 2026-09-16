r"""G29 F14 — omitted POSITIONAL constructor argument with an INT default"""
from dataclasses import dataclass, field
from typing import NamedTuple
_ = 0  # anchor


class Cy:
    def __init__(self, r: int = 5) -> None:
        self.r = r


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
