from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns \nothing
    def __gt__(self, other: object) -> bool:
        return False

    #@ assigns \nothing
    def __lt__(self, other: object) -> bool:
        return False

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __add__(self, x: int) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __bool__(self) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __neg__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return (-max(o, o))


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.v


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
