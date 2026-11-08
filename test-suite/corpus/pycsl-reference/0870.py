"""Test 0870 — WL-07 regression lock (NEGATIVE twin of 0869). # pycsl-expected: FAIL

The headline soundness lock for the `@dataclass` constructor arg-drop unsoundness.
Before the fix, a `@dataclass` DROPPED its positional constructor arguments, so
`Point(1, 2)` emitted `{ x = 0; y = 0 }` and `arg_drop_UNSOUND` — which builds
`Point(1, 2)` and returns `p.x` (== 1) but CLAIMS `\result == 0` — PROVED. That is a
green proof of a claim FALSE of real Python (`Point(1, 2).x` is `1`, never `0`).

With the WL-07 fix the ctor binds `x` from the first positional arg, so `p.x == 1`
and the false `== 0` claim is UNPROVEN. If this test ever PASSES again, the
dataclass constructor has regressed to dropping its args — the severity-1
unsoundness is back.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def arg_drop_UNSOUND() -> int:
    """Returns Point(1, 2).x (== 1) but claims == 0 (the old field-default). FALSE."""
    p = Point(1, 2)
    return p.x


if __name__ == "__main__":
    # Point(1, 2).x == 1, but the contract claims == 0. FALSE.
    assert arg_drop_UNSOUND() == 1
