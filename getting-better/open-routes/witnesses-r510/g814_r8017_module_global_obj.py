from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 1


g = C()


#@ no_exception \all
def f() -> int:
    return g.v


type g = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
