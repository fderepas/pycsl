from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, n: int) -> None:
        if n > 0:
            self.x = 1

    def g(self) -> int:
        return self.x



#@ no_exception \all
def f(n: int) -> int:
    return P(n).g()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
