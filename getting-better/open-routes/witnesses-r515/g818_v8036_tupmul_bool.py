from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    w = bool((lambda m: (1,) * m)(n))
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20, "ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
