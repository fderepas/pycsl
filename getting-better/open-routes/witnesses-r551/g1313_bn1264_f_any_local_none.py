from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: str) -> None:
        self.n = len(s)


#@ no_exception \all
def f(k: int) -> int:
    v: Any = None
    c = C(v)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
