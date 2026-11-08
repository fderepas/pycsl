from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    k = None

    def __init__(self, n: int) -> None:
        self.j = self.k + 1


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
