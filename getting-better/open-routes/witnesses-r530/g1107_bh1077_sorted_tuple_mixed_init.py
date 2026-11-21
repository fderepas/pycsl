from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, t: Tuple[int, str]) -> None:
        self.k = sorted(t)


#@ no_exception \all
def f(t: Tuple[int, str]) -> int:
    c = C(t)
    return 1


if __name__ == "__main__":
    try:
        r = f((1, "a"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
