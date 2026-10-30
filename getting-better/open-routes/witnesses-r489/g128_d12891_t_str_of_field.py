from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return 'c'


class E:
    def __init__(self, o: C) -> None:
        self.o = o


#@ \trusted
def k(e: E) -> int:
    return len(str(e.o))


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    e = E(o)
    k(e)
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
