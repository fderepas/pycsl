from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def f(n: int) -> int:
    return 1 if (n * 3) is (n * 3) else 0


if __name__ == "__main__":
    try:
        r = f(500)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
