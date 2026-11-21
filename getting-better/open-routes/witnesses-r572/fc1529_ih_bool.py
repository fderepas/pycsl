from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
#@ assigns \nothing
def f(x) -> int:
    name = x
    name = ""
    if name:
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(3)
        print("VIOLATION contract" if r != 1 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
