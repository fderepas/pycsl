r"""Test 7830 -- cross-mixin-declaration-stubs B4 (expected FAIL: REFUSED near-miss, route #463 class): `# @declared_in other.py::B.m` (a space between `#` and `@`) is a plain comment to the tokenizer; `declared_in` is in the ingestor's directive-keyword list, so the near-miss is refused instead of silently discarded. Every contract here is TRUE (`m` returns 1): without the near-miss refusal the file would PROVE, so the FAIL is the refusal and nothing else; CPython returns 1.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    # @declared_in other.py::B.m
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.m()
