r"""HAPPY protects: direct write to a protected path from a non-exempt method."""
# pycsl-flags: --memory-model hoare
from typing import List


#@ happy own:
#@     protects self.log
#@     except append_entry
class S:
    def __init__(self) -> None:
        self.log: List[int] = [0]

    #@ assigns self.log
    def append_entry(self) -> None:
        self.log[0] = 1

    #@ assigns self.log
    def tamper(self) -> None:
        self.log[0] = 9


#@ ensures \result == 0
def probe() -> int:
    s = S()
    s.tamper()
    return s.log[0]


if __name__ == "__main__":
    print("CPython:", probe())
