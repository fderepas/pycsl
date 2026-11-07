r"""Test 8305 -- route #519 (control, expected PASS): a @dataclass `__post_init__` deriving a field from a declared `int` field by `*` / `+` of small literals; CPython f(4) returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    n: int
    k: int = 0

    def __post_init__(self) -> None:
        self.k = self.n * 2 + 1


#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    p = P(n)
    return 1


if __name__ == "__main__":
    print(f(4))
