from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def hs(x: str) -> int:
    return len(x + "c")



#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    return max((hs(x) for x in xs), default=0)


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
