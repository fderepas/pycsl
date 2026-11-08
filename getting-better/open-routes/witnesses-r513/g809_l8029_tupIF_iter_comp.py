from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[int, float]) -> int:
    v = [a * 0.5 for a in t]
    return 1


if __name__ == "__main__":
    try:
        r = f((10**400, 0.5))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
