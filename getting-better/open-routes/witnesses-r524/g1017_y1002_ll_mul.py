from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xss) >= 1 and len(xss[0]) >= 1
#@ no_exception \all
def f(xss: List[List[Optional[int]]]) -> int:
    return xss[0][0] * 2


if __name__ == "__main__":
    try:
        r = f([[None]])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
