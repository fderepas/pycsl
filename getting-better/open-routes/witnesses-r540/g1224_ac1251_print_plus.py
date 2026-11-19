from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


def noret(k: int) -> None:
    k2 = k



#@ no_exception \all
def f(k: int) -> int:
    xs: List[int] = [2, 1]
    d: Dict[str, int] = {}
    s: Set[int] = set()
    w = +print("x")
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
