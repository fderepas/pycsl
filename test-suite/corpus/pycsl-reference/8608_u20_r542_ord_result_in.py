r"""Test 8608 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND; executor u20 probe beyond the red-team family): `1 in ord("a")`, a builtin of fixed int result as a haystack; CPython f(3) -> TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class P:
    a: int


class Box:
    def __init__(self) -> None:
        self.items: List[str] = []


#@ no_exception \all
def f(k: int) -> int:
    return 1 if 1 in ord("a") else 0


if __name__ == "__main__":
    try:
        print(f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
