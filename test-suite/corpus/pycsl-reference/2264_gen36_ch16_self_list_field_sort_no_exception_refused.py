r"""Test 2264 — gen #36 ch16 (expected FAIL): `list.sort` raises `TypeError` on mixed
element types (and a key may raise anything), and the in-place havoc carries no exception
trigger, so a function that declares any `#@ no_exception` (here `\all`) keeps the
in-place-mutator REFUSAL.
CPython: `Box([1, "a"]).order()` raises TypeError. This file is `pycsl-expected: FAIL`:
the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class Box:
    xs: List[int] = field(default_factory=list)

    #@ no_exception \all
    #@ assigns self.xs
    def order(self) -> None:
        self.xs.sort()


if __name__ == "__main__":
    try:
        Box([1, "a"]).order()
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
