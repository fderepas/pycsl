from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class L:
    def __len__(self) -> int:
        return -1


class C:
    def __init__(self, n: int) -> None:
        self.b = 1 if L() else 0


#@ no_exception \all
def f(k: int) -> int:
    c = C(k)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
