"""Advice of PYCSL-R461-IMPORT-RAISES followed on 7147: the class made exception-free (`field(default_factory=list)`)."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass, field

@dataclass
class P:
    xs: List[int] = field(default_factory=list)



#@ no_exception \all
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
