from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(a: List[int]) -> int:
    for i in range(2):
        a *= 2
    return len(a)


if __name__ == "__main__":
    try:
        r = f([1])
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
