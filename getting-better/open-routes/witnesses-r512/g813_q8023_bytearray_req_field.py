from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Buf:
    def __init__(self, n: int) -> None:
        self.data = bytearray(n)


#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    k = Buf(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
