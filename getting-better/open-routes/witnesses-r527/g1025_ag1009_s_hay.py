from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    x: int


@dataclass
class R:
    o: Optional[C]
    v: Optional[int]
    s: Optional[str]
    d: Dict[str, Optional[int]]
    xs: List[Optional[int]]


#@ no_exception \all
def f(r: R) -> int:
    return 1 if "a" in r.s else 0


if __name__ == "__main__":
    try:
        r = f(R(None, None, None, {"k": None}, [None]))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
