from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


#@ no_exception \all
def f(d: Dict[str, int], k: str, os_: List[Optional[int]], ys: List[int], o: Optional[int] = None) -> int:
    if len(ys) < 2:
        return 0
    ys[0:1] = [None]
    return ys[0] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a", [None], [1, 2])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
