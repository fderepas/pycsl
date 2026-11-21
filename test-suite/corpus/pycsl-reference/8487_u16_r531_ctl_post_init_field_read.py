r"""Test 8487 -- route #531 (control, expected PASS): a dataclass field read in `__post_init__` (set by the synthesized `__init__`) resolves; CPython f(2) returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class D:
    a: int

    def __post_init__(self) -> None:
        self.b = self.a


#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    d = D(n)
    return 1


if __name__ == "__main__":
    print(f(2))
