from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

OPS = ["abc", "defg"]


#@ ensures \result == 0
def f(k: int) -> int:
    for x in OPS:
        if x == "z":
            return 1
    return 0

import __main__
__main__.OPS.append("z")


if __name__ == "__main__":
    try:
        r = f(0)
        print("VIOLATION contract", r) if r != 0 else print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
