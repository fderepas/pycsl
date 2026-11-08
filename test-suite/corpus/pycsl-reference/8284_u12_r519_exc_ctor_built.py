r"""Test 8284 -- route #519 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g927/l9006_exc_ctor_built.py): a user exception `__init__` storing `len("ab" * n)`, built not raised; the constructor is lowered to a record literal and its body never judged; CPython raises OverflowError at f(10**20)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class E(Exception):
    def __init__(self, n: int) -> None:
        super().__init__()
        self.k = len("ab" * n)


#@ no_exception \all
def f(n: int) -> int:
    e = E(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
