from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    name = x
    name = "abc"
    return name + 1


if __name__ == "__main__":
    try:
        print("result", f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
