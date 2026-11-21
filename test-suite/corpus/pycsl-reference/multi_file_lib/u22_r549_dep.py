"""Helper for corpus 8660-8673 (route #549): int-parameter callees of a program module."""
from typing import Optional


#@ no_exception \all
def g(x: int) -> int:
    return x + 1


#@ no_exception \all
def gd(x: int = 0) -> int:
    return x * 2


#@ no_exception \all
def hopt(x: Optional[int]) -> int:
    if x is None:
        return 0
    return x


class DC:
    #@ no_exception \all
    def __init__(self, x: int) -> None:
        self.x = x + 1
