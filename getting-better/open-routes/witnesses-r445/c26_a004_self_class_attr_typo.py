from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    k = 1

    def __init__(self) -> None:
        self.x = 1

    def g(self) -> int:
        return self.kk



#@ no_exception \all
def f(n: int) -> int:
    return P().g()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
