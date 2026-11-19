from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int], k: str, ys: List[int]) -> int:
    xs = [1, 2]
    xs[0:1] = [d.get(k)]
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a", [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
