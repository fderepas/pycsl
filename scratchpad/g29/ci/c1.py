r"""subclass method breaks inherited invariant"""
from typing import List
_ = 0  # anchor


#@ class invariant self.x >= 0
class A:
    def __init__(self) -> None:
        self.x = 0

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


class B(A):
    #@ assigns self.x
    def breakit(self) -> None:
        self.x = -1


#@ ensures \result >= 0
def probe() -> int:
    b = B()
    b.breakit()
    return b.get()


if __name__ == "__main__":
    print("CPython:", probe())
