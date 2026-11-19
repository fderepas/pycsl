from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __eq__(self, other: object) -> bool:
        self.v = 7
        return True

    #@ assigns self.v
    def __add__(self, x: int) -> int:
        self.v = 7
        return 1


class K:
    #@ \trusted
    def __init__(self, o: C) -> None:
        self.r = len(o)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    K(o)
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
