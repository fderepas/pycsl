from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, x: int) -> None:
        self.x = x

    def helper(self) -> int:
        return 1

    def g(self) -> int:
        return self.helpr()



#@ no_exception \all
def f(p: P) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
