from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import h9600p
import h9600


#@ ensures \result == n
def f(n: int) -> int:
    return h9600.g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
