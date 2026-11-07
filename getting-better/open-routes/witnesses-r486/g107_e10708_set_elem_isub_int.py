from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires len(a) == 1
#@ no_exception \all
def f(a: List[Set[int]]) -> int:
    a[0] -= 1
    return 0


if __name__ == "__main__":
    try:
        r = f([{1}])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
