"""Helper for corpus 8674-8680 (route #554): signatures of a program module's callables."""
from dataclasses import dataclass
from typing import NamedTuple


#@ no_exception \all
def g(x: int) -> int:
    return x + 1


#@ no_exception \all
def gd(x: int, y: int = 0) -> int:
    return x + y


@dataclass
class DD:
    a: int


class NT(NamedTuple):
    a: int


class PC:
    #@ no_exception \all
    def __init__(self, a: int) -> None:
        self.a = a
