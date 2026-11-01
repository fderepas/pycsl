from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f() -> int:
    k = 0
    for i in range(3):
        type i = int
        k += i
    return k


if __name__ == "__main__":
    try:
        r = f()
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
