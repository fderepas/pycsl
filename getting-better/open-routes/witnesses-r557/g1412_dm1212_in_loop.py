from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Set[int]



#@ no_exception \all
def f(k: int, s: Set[int], ws: Set[str], xs: List[int], r: R) -> int:
    for i in range(2):
        s[i] = i
    return 1


if __name__ == "__main__":
    try:
        r = f(1, {1, 2}, {"a"}, [1, 2], R({1}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
