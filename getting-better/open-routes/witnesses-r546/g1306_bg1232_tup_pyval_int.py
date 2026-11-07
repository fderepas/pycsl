from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, Any, int]:
    return (1, 2, None)


#@ no_exception \all
def f(d: Dict[str, int], k: str) -> int:
    t = g(1)
    return t[2] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a")
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
