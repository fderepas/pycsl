from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
    return 1 if isinstance(d, dict) else 0


#@ ensures \result == 1
def h() -> int:
    return g(3)


if __name__ == "__main__":
    try:
        r = h()
        if not (r == 1):
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
