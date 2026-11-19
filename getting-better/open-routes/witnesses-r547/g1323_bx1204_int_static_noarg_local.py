from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int


class Q:
    @staticmethod
    def m() -> int:
        return None


#@ no_exception \all
def f(k: int) -> int:
    v = Q.m()
    return v + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
