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


@mutable_state
class S(C):

    #@ requires True
    #@ ensures True
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v
        self.flag = v


#@ requires True
#@ ensures True
#@ assigns s.a
def touch(s: S) -> None:
    s.m(1)


#@ requires True
#@ ensures \result == 1
#@ assigns c.a
def caller(c: C, o: Any, s: S) -> int:
    touch(s)
    c.m(0)
    x = getattr(o, "flag", 0)
    c.m(5)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2
