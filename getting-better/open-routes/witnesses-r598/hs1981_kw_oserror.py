from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise OSError("a", q=1)
    except OSError:
        return 1
    return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
