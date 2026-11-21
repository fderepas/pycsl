from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
#@ assigns xs
def f(xs: List[int], b: int) -> int:
    if not xs:
        return 0
    xs[0] @= b
    return 1


if __name__ == "__main__":
    try:
        r = f([1], 2)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
