from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(xs: List[int]) -> None:
    for i in range(len(xs)):
        xs[i] = None


#@ no_exception \all
def f(k: int) -> int:
    xs = [1, 2]
    g(xs)
    return xs[1] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
