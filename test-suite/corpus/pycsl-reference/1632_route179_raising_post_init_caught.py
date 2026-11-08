r"""Test 1632 - ROUTE #179 (gen #29): a dataclass whose `__post_init__` raises ValueError, constructed as `P(-1)` inside `try ... except ValueError: return 9`, PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    v: int

    def __post_init__(self) -> None:
        if self.v < 0:
            raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        p = P(-1)
    except ValueError:
        return 9
    return 0
