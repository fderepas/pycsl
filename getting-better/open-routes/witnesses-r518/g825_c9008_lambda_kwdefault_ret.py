from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K


_l = lambda *, a=(K := 0): a


if __name__ == "__main__":
    try:
        r = f()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
