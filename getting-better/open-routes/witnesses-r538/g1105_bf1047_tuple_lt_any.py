from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[int, Any], u: Tuple[int, Any]) -> int:
    return 1 if t < u else 0


if __name__ == "__main__":
    try:
        r = f((1, "a"), (1, 2))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
