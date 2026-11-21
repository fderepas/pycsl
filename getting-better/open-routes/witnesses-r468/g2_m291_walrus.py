from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h291 import g


#@ requires \length(a) == 2
#@ ensures \result == 2
def f(a: List[int]) -> int:
    g(a)
    return len(a)


if __name__ == "__main__":
    try:
        r = f([0, 0])
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
