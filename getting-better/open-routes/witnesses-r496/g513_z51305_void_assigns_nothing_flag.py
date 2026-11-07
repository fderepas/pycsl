from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ assigns \nothing
def g(s: str) -> None:
    y = s.index("z")


#@ ensures \result == 1
def f(s: str) -> int:
    r = 1
    try:
        g(s)
    except ValueError:
        r = 2
    return r


if __name__ == "__main__":
    try:
        r = f('a')
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
