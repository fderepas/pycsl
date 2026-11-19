from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self) -> None:
        self.count = 1

    def g(self) -> int:
        return self.cout



#@ no_exception \all
def f(p: P) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(P())
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
