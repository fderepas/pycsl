from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum
from typing import NamedTuple


class MyInt(int):
    pass


class MyFloat(float):
    pass


class K:
    pass


class KI:
    def __init__(self, a: int) -> None:
        self.a = a


class Fl(enum.Flag):
    R = 1


class IF(enum.IntFlag):
    R = 1



#@ no_exception \all
def f(k: int) -> int:
    return sum(1 for x in KI(k))


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
