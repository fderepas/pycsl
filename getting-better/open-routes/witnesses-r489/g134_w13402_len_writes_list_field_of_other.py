from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class D:
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs

    #@ \trusted
    #@ assigns self.xs
    def __len__(self) -> int:
        self.xs.append(1)
        return 1


#@ \trusted
def k(o: D) -> int:
    return len(o)


#@ ensures \result == 1
def f(n: int) -> int:
    a = [0]
    o = D(a)
    k(o)
    return len(a)


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
