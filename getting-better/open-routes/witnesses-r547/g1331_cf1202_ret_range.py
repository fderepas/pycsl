from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> int:
    return None


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f(k: int) -> int:
    n = 0
    for i in range(g(k)):
        n += 1
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
