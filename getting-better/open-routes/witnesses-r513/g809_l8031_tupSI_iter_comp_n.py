from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[str, int], n: int) -> int:
    v = [a * n for a in t]
    return 1


if __name__ == "__main__":
    try:
        r = f(("ab", 1), 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
