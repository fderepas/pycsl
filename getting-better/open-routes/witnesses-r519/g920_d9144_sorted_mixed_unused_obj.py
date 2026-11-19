from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = len(sorted([n, "a"]))


#@ no_exception \all
def f(n: int) -> int:
    C(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:40])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
