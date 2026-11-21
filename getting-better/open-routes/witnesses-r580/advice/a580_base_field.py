from typing import Any


def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0
        self.flag: int = 0

    #@ ensures self.flag == v
    #@ assigns self.a, self.flag
    def m(self, v: int) -> None:
        self.a = v
        self.flag = v


@mutable_state
class S(C):

    #@ ensures self.flag == v
    #@ assigns self.a, self.flag
    def m(self, v: int) -> None:
        self.a = v + 1
        self.flag = v


#@ ensures \result == 1
#@ assigns c.a, c.flag
def caller(c: C) -> int:
    c.m(0)
    x = c.flag
    c.m(5)
    y = c.flag
    if x == 0 and y == 5:
        return 1
    return 2


if __name__ == "__main__":
    print("result", caller(S()), caller(C()))
