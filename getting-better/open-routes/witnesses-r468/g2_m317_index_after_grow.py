from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h317 import g


#@ requires \length(a) == 2
#@ ensures \result == 0
def f(a: List[int]) -> int:
    g(a)
    if len(a) > 2:
        return 1
    return 0


if __name__ == "__main__":
    try:
        r = f([0, 0])
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
