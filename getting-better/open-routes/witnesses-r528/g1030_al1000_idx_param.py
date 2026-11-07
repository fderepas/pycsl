from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires i >= 0
#@ no_exception \all
def f(s: str, i: int) -> int:
    return len(s.split(",")[i])


if __name__ == "__main__":
    try:
        r = f("ab", 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
