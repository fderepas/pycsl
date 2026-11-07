from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures "a" in d
def g(d: Dict[str, int]) -> None:
    d["a"] = None


#@ no_exception \all
def f(k: int, ys: List[int]) -> int:
    d = {"a": 1}
    g(d)
    return d.get("a", 0) + 1


if __name__ == "__main__":
    try:
        r = f(1, [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
