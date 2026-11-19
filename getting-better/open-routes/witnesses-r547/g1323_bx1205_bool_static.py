from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int


class Q:
    @staticmethod
    def m(k: int) -> bool:
        return None


#@ no_exception \all
def f(k: int) -> int:
    return 1 if Q.m(k) + 1 > 0 else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
