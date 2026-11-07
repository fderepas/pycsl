r"""Test 4883 -- gen #37 route #361: CONTROL: dataclass with `InitVar` and `KW_ONLY`, reads of the REAL fields only; PROVES (CPython 4).
"""
from dataclasses import dataclass, InitVar, KW_ONLY

@dataclass
class D:
    x: int
    k: InitVar[int]
    _: KW_ONLY
    y: int = 0

#@ ensures \result == 4
def f() -> int:
    d = D(1, 9, y=3)
    return d.x + d.y

if __name__ == "__main__":
    print(f())
