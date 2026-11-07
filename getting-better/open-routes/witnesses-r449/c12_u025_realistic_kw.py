from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def total(items: List[int], initial: int = 0) -> int:
    s = initial
    for x in items:
        s += x
    return s



#@ no_exception \all
def f(items: List[int]) -> int:
    return total(items, start=1)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
