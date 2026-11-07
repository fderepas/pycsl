from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int], o: Optional[int] = None) -> int:
    return sum(1 for x in xs if ~xs)


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
