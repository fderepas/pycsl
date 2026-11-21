r"""Test 6021 -- gen #37 route #404 (expected PASS): CONTROL: a metaclass deriving from `type` that defines nothing, and `metaclass=abc.ABCMeta` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import abc


class M(type):
    "A metaclass that defines nothing."


class K(metaclass=M):
    def __init__(self) -> None:
        self.x: int = 1


class P(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        self.y: int = 2


#@ no_exception \all
#@ ensures \result == 1
def f(k: K, p: P) -> int:
    return 1


if __name__ == "__main__":
    print(f(K(), P()))
