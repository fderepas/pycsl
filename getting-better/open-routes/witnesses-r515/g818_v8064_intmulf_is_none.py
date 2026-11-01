from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int, s: str) -> int:
    w = (lambda m: m * 0.5)(n) is None
    return 1


if __name__ == "__main__":
    try:
        r = f(10**400, "ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
