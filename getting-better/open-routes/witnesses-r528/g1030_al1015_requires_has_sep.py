from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires "," in s
#@ no_exception \all
def f(s: str) -> int:
    return len(s.split(",")[2])


if __name__ == "__main__":
    try:
        r = f("a,b")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
