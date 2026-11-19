from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(s: str) -> int:
    y = s.partition(",")[2].index("z")
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return g(s)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f('a,b')
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
