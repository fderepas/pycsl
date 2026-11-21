from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def m(self) -> int:
        v = {len(range(self.n))}
        return 1


#@ no_exception \all
def f(n: int) -> int:
    k = K(n)
    return k.m()


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
