from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, o: object) -> None:
        self.k = o.nope


class W:
    def __init__(self, o: object) -> None:
        self.c = C(o)


#@ no_exception \all
def f(o: object) -> int:
    w = W(o)
    return 1


if __name__ == "__main__":
    try:
        r = f(object())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
