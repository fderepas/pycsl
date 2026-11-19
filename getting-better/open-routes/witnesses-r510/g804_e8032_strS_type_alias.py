from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import sys

S = "a"


#@ ensures \result == 1
#@ no_exception \all
def f() -> int:
    return len(S)


type S = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
