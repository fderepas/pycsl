from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == K
def f() -> int:
    return 5

type K = int


if __name__ == "__main__":
    try:
        r = f() == K
        if r != True:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
