from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional


#@ no_exception \all
def gd(x: int, y: int = 0) -> int:
    return x + y


#@ no_exception \all
def g0() -> int:
    return 1


@dataclass
class DD:
    a: int


@dataclass
class DD2:
    a: int
    b: int = 0


class NT(NamedTuple):
    a: int


class PC:
    #@ no_exception \all
    def __init__(self, a: int) -> None:
        self.a = a

    #@ no_exception \all
    def m(self, y: int) -> int:
        return self.a + y
