from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ ensures \result <= a
def f(a: int, b: int) -> int:
    return min(a, b, default=a)


if __name__ == "__main__":
    try:
        r = f(3, 4)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
