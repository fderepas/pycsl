from typing import Dict, List, Optional


#@ no_exception \all
def g(x: int) -> int:
    return x + 1


#@ no_exception \all
def g2(x: int, y: int) -> int:
    return x + y


#@ no_exception \all
def gkw(x: int, *, y: int) -> int:
    return x + y


#@ no_exception \all
def gpos(x: int, /) -> int:
    return x


class DC:
    #@ no_exception \all
    def __init__(self, x: int) -> None:
        self.x = x

    #@ no_exception \all
    def m(self, y: int) -> int:
        return self.x + y
