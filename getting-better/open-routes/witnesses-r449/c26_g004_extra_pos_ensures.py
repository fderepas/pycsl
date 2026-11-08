from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(a: int) -> int:
    return a



#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return g(n, 5)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
