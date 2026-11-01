from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ \abstract
#@ ensures \result == 1
def g() -> int: ...


#@ no_exception \all
def f(n: int) -> int:
    return g() + 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
