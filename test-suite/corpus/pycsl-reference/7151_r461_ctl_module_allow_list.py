r"""Test 7151 -- route #461 (expected PASS): CONTROL -- a module whose top level and class bodies are all on the exception-free allow-list: imports, constants and container literals, `re.compile` / `frozenset` / `os.path.join` of literals, typing aliases, an `if TYPE_CHECKING:` import, a `try` import whose body cannot raise, an identity class decorator, Enum / IntEnum (a nested class), NamedTuple, dataclasses (a `default_factory`, frozen-from-frozen, `order=True` without a user `__lt__`), `__slots__`, a field-initialiser global instance, and the `__main__` driver. CPython imports it cleanly; PROVED at base and candidate.
"""
# pycsl-expected: PASS
import os
import re
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Tuple

if TYPE_CHECKING:
    from collections import OrderedDict

LIMIT = 10
MASK = (1 << 8) - 1
NAMES: Tuple[str, ...] = ("a", "b")
TABLE: Dict[str, int] = {"a": 1, "b": 2}
KEYS = frozenset(TABLE)
WORD = re.compile(r"[a-z]+")
SEP = os.path.join("a", "b")
Pair = Tuple[int, int]
try:
    import json
except ImportError:
    pass


def mutable_state(cls):
    return cls


class Color(Enum):
    RED = 1
    GREEN = 2


class Level(IntEnum):
    LOW = 1

    class Meta:
        pass


class Point(NamedTuple):
    x: int
    y: int = 0


@mutable_state
@dataclass
class Box:
    w: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True, order=True)
class Key:
    k: int


@dataclass(frozen=True)
class SubKey(Key):
    j: int = 0


class Slotted:
    __slots__ = ("a",)

    def __init__(self, a: int) -> None:
        self.a = a


class Tally:
    def __init__(self) -> None:
        self.n = 0


_t = Tally()


#@ requires 0 <= n
#@ ensures \result == n + LIMIT
#@ no_exception \all
def f(n: int) -> int:
    return n + LIMIT


if __name__ == "__main__":
    print(f(1))
