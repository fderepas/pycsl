from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

S = "ab"


#@ ensures \result == 2
def f() -> int:
    return len(S)


_l = lambda a=(S := "abc"): a


if __name__ == "__main__":
    try:
        r = f()
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
