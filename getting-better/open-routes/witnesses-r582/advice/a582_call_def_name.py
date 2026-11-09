from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    K = 3
    n = 0
    L: int = -1


#@ requires c.a == 0
#@ ensures \result == 5
#@ assigns c.a
def caller(c: C) -> int:
    c.m(5)
    return c.a


if __name__ == "__main__":
    print("result", caller(C()))
