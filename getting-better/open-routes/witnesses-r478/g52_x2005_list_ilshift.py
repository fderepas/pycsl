from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ assigns \nothing
def f(a: List[int]) -> int:
    a <<= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
