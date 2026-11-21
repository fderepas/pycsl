from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class B:
    def __init__(self) -> None:
        self.a = 1


class Q(B):
    def __init__(self, n: int) -> None:
        self.b = n

    def g(self) -> int:
        return self.a + self.b



#@ no_exception \all
def f(n: int) -> int:
    return Q(n).g()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
