from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.a
    def g(self, o: Any) -> int:
        self.m(0)
        x = getattr(o, "flag", 0)
        self.m(5)
        y = getattr(o, "flag", 0)
        if x or not y:
            return 1
        return 2


@mutable_state
class S(C):

    #@ requires True
    #@ ensures True
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v
        self.flag = v
