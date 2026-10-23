r"""HAPPY protects: write through a method of ANOTHER class holding the object."""
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


class T:
    def __init__(self) -> None:
        self.s = S()

    #@ assigns self.s
    def tamper(self) -> None:
        self.s.log[0] = 9


#@ ensures \result == 0
def probe() -> int:
    t = T()
    t.tamper()
    return t.s.log[0]


if __name__ == "__main__":
    print("CPython:", probe())
