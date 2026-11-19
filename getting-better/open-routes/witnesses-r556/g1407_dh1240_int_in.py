from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import math
import os



#@ no_exception \all
def f(k: int, xs: List[int]) -> int:
    return 1 if k in int else 0


if __name__ == "__main__":
    try:
        r = f(1, [1, 2])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
