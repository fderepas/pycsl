from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class E:
    m: str

#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int], d: Dict[str, int], k: int, s: str) -> int:
    try:
        raise E("a")
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f([1], {"a": 1}, 0, "ab")
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
