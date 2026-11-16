# u47: a parameter named `int` shadows the builtin inside the sha-256 digest model:
# `int(<digest>, 16)` is the user callable, which raises KeyError (the model: ValueError only).
from __future__ import annotations
import hashlib
from typing import Callable


#@ no_exception KeyError
def h(s: str, int: Callable[[str, int], int]) -> int:
    try:
        return int(hashlib.sha256(s.encode()).hexdigest(), 16)
    except ValueError:
        return 0
    except UnicodeEncodeError:
        return 0


def _kx(s: str, b: int) -> int:
    d = {"a": 1}
    return d[s]


if __name__ == "__main__":
    try:
        print("result", h("abc", _kx))
    except KeyError as e:
        print("VIOLATION no_exception KeyError", e)
