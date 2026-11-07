from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self) -> None:
        self.x = 1



#@ no_exception \all
def f(p: P, n: int) -> int:
    return p.x @ n


if __name__ == "__main__":
    try:
        r = f(P(), 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
