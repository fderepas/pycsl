from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ no_exception \all
def f(n: int) -> int:
    return n // K

if True:
    type K = int


if __name__ == "__main__":
    try:
        r = f(10)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
