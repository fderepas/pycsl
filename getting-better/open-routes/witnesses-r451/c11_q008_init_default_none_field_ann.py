from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, s: Optional[str] = None) -> None:
        self.s: str = s  # type: ignore



#@ no_exception \all
def f(n: int) -> int:
    return len(P().s.upper())


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
