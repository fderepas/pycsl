r"""Test 8643 -- route #547 (control, expected PASS): `Q.m(k) + 1` and `Q().n(k) + 1` of an int staticmethod / method that never returns None
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    def __init__(self) -> None:
        self.a = 1

    @staticmethod
    #@ requires 0 <= k <= 1000
    #@ ensures \result == k
    def m(k: int) -> int:
        return k

    #@ requires 0 <= k <= 1000
    #@ ensures \result == k
    def n(self, k: int) -> int:
        return k


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    q = Q()
    a = Q.m(k)
    b = q.n(k)
    return a + b + 1


if __name__ == "__main__":
    print("result", f(3))
