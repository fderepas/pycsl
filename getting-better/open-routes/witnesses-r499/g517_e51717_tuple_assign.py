from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 12
def f(n: int) -> int:
    a = 0
    b = 0
    exec("a, b = 1, 2")
    return a * 10 + b


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 12):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
