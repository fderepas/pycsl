from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    b = bytes(n)
    if n > 0:
        return b[0]
    return 0


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
