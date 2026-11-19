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
        self.flag = v

    n = m


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def caller(c: Any, o: Any) -> int:
    c.n(0)
    x = getattr(o, "flag", 0)
    c.n(5)
    y = getattr(o, "flag", 0)
    if x or not y:
        return 1
    return 2


if __name__ == "__main__":
    try:
        k = C()
        r = caller(k, k)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
