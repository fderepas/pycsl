from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


def nothing() -> None:
    return None



#@ no_exception \all
def f(k: int) -> int:
    a: List[str] = []
    d = {"x": 1}
    a.append(d["x"])
    return sum([len(p) for p in a])


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
