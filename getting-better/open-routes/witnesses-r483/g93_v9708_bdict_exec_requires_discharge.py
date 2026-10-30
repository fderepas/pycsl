from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h9708 import K


#@ requires k == 1
#@ ensures \result == 1
def g(k: int) -> int:
    return k


#@ ensures \result == 1
def f(n: int) -> int:
    return g(K)


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
