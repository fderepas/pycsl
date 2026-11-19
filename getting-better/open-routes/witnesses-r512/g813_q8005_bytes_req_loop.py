from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    b = bytes(n)
    k = 0
    for x in b:
        k += x
    return k


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
