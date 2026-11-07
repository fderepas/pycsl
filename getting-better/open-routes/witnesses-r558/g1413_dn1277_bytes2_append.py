from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, ys: List[str]) -> int:
    xs: List[int] = [1]
    xs.append(bytes(2))
    x = xs[1]
    return x + 1


if __name__ == "__main__":
    try:
        r = f(1, "ab", ["a"])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
