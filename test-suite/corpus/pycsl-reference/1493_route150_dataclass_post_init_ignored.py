r"""Test 1493 - ROUTE #150 (gen #29): `@dataclass class P: x: int` with `__post_init__` storing `self.x = 7`; the synthesized constructor's record literal was `{ x = 1 }` and `P(1).x == 1` PROVED; CPython 7. A class whose constructor runs a `__post_init__` is now OPAQUE (every field unknown).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int

    def __post_init__(self) -> None:
        self.x = 7


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    return p.x

