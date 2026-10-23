r"""interface assigns narrower than definition"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.a = 0
        self.b = 0

    #@ assigns self.a, self.b
    #@ interface assigns self.a
    def m(self) -> None:
        self.a = 1
        self.b = 2


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.m()
    return c.b


if __name__ == "__main__":
    print("CPython:", probe())
