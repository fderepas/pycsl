from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, x: float) -> None:
        self.k = {y: 1 for y in x}


#@ no_exception \all
def f(x: float) -> int:
    c = C(x)
    return 1


if __name__ == "__main__":
    try:
        r = f(1.5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
