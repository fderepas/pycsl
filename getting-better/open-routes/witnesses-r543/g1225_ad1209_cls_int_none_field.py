from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class P:
    def __init__(self, a: int) -> None:
        self.a = a



#@ no_exception \all
def f(k: int) -> int:
    x: P = None
    return x.a


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
