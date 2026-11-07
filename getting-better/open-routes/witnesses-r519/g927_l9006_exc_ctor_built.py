from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class E(Exception):
    def __init__(self, n: int) -> None:
        super().__init__()
        self.k = len("ab" * n)


#@ no_exception \all
def f(n: int) -> int:
    e = E(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
