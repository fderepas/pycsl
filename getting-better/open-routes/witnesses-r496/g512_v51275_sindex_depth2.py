from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(s: str) -> int:
    y = s.index("z")
    return 1


#@ ensures \result == 1
def h(s: str) -> int:
    return g(s)


class K:
    #@ ensures \result == 1
    def m(self, s: str) -> int:
        y = s.index("z")
        return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return h(s)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f('a')
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
