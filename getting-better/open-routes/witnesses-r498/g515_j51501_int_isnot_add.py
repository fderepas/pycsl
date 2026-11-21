from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == False
def f(n: int) -> bool:
    return (n + 1) is not (n + 1)


if __name__ == "__main__":
    try:
        r = f(1000)
        if not (r == False):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
