from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == 0
def f(n: int) -> int:
    return __file__ * 0


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
