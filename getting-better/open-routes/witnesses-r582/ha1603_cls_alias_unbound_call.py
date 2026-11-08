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
    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    n = m


#@ requires True
#@ ensures True
#@ assigns c.a
def g(c: C, v: int) -> None:
    c.a = v



#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    C.n(c, 5)
    return c.a


if __name__ == "__main__":
    try:
        r = caller(C())
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
