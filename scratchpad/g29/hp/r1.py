r"""HAPPY region integrity: write inside the region from a non-exempt method through an alias."""
# pycsl-flags: --memory-model hoare
from typing import List


#@ happy region_integrity:
#@     region 2 .. 4
#@     writes self.disk outside region
#@     except setup
class S:
    def __init__(self) -> None:
        self.disk: List[int] = [0, 0, 0, 0, 0, 0]

    #@ assigns self.disk
    def setup(self) -> None:
        self.disk[2] = 1

    #@ assigns self.disk
    def poke(self) -> None:
        d = self.disk
        d[3] = 9


#@ ensures \result == 0
def probe() -> int:
    s = S()
    s.poke()
    return s.disk[3]


if __name__ == "__main__":
    print("CPython:", probe())
