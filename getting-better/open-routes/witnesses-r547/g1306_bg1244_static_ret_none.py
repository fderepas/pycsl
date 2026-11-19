from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    @staticmethod
    def m() -> int:
        return None


#@ no_exception \all
def f(d: Dict[str, int], k: str, ys: List[int]) -> int:
    return Q.m() + 1


if __name__ == "__main__":
    try:
        r = f({}, "a", [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
