from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, n: int) -> int:
    zs: List[int] = []
    v = sorted((s * n, s * n))
    return 1


if __name__ == "__main__":
    try:
        r = f('a' * 1000, 10**16)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
