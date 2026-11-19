from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[int, object]:
    return (1, None)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return 1 if k > t[1] else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
