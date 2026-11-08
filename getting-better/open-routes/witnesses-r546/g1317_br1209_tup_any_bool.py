from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, bool]:
    return (k, None)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return 1 if t[1] + 1 > 0 else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
