r"""Test 5592 -- gen #37 route #395 (expected PASS): CONTROL: a base B hashed by `{b}` whose every file subclass is hashable: a plain subclass, a frozen `@dataclass` subclass, and a subclass whose own `__hash__` is a VERIFIED `no_exception \all` method (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


class B:
    def __init__(self) -> None:
        self.x: int = 1


class S1(B):
    pass


@dataclass(frozen=True)
class S2(B):
    y: int = 0


class S3(B):
    #@ no_exception \all
    #@ assigns \nothing
    def __hash__(self) -> int:
        return 7


#@ no_exception \all
#@ ensures \result == 1
def f(b: B) -> int:
    s = {b}
    return 1


if __name__ == "__main__":
    print(f(B()), f(S1()), f(S2()), f(S3()))
