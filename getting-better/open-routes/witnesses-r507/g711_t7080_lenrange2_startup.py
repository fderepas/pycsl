from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(a: int, b: int) -> int:
    zs: List[int] = []
    v = (*zs, len(range(a, b)))
    return 1


if __name__ == "__main__":
    try:
        r = f(-10**20, 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
