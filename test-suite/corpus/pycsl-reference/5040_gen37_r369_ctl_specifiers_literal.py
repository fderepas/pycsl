r"""Test 5040 -- gen #37 route #369 (expected PASS): CONTROL: literal `ClassVar` (via `t.ClassVar`), `InitVar`, `KW_ONLY`, `field(init=False)`; `D(1, 5, y=2).x == 1` (CPython ok).
"""
# pycsl-expected: PASS
import typing as t
from dataclasses import dataclass, field, InitVar, KW_ONLY


@dataclass
class D:
    x: int
    k: t.ClassVar[int] = 3
    iv: InitVar[int] = 0
    _: KW_ONLY
    y: int = 4
    z: int = field(default=6, init=False)


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    d = D(1, 5, y=2)
    return d.x


if __name__ == "__main__":
    print(f())
