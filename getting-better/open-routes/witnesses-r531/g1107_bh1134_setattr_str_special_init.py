from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: str) -> None:
        setattr(self, s, 1)
        self.k = 1


#@ no_exception \all
def f(s: str) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    try:
        r = f("__dict__")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
