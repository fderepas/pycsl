from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, x: float, s: str) -> None:
        match s:
            case x:
                pass
        self.k = x / 2


#@ no_exception \all
def f(x: float, s: str) -> int:
    c = C(x, s)
    return 1


if __name__ == "__main__":
    try:
        r = f(1.5, "a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
