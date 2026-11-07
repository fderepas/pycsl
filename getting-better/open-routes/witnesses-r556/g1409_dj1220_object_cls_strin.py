from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os
import functools



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int]) -> int:
    return 1 if t in object else 0


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
