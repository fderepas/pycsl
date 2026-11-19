from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 2
def f(s: str) -> int:
    t = "a"
    exec("t = 'bb'")
    return len(t)


if __name__ == "__main__":
    try:
        r = f('')
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
