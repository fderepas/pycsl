"""Test 0869 — WL-07 regression lock (POSITIVE, faithful `@dataclass` constructor):
a `@dataclass` with NO explicit `__init__` now binds each field from the
same-position positional argument in field-DECLARATION order — plus the keyword
form `Point(x=1, y=2)`, the mixed form `Point(1, y=2)`, and a partial call whose
trailing defaulted field keeps its default.

Before the fix (severity-1 UNSOUND, fail-OPEN): Python's `@dataclass` synthesizes
`__init__(self, x, y)` binding each declared field positionally, but PyCSL's
`_collect_init_construction` only walked an EXPLICIT `__init__`, so a dataclass got
empty `init_params`/`init_body` and `_call_record_constructor` fell EVERY field to
its zero default. So `Point(1, 2)` emitted `{ x = 0; y = 0 }` and `Point(1, 2).x
== 0` PROVED — FALSE of real Python (`.x` is `1`). Keyword args were DROPPED from
the Call IR entirely, so `Point(x=1, y=2)` was likewise all-defaults.

PyCSL now synthesizes the dataclass ctor's `init_params`/`init_body` (the fields in
declaration order, `self.f = f`), mirroring the NamedTuple record path, and captures
keyword args in `CallExpr.keywords` — so `_call_record_constructor` threads
positional and keyword args into the fields. Ground truth: `Point(1, 2).x == 1`,
`.y == 2`; `Point(x=1, y=2).x == 1`; `Point(1, y=2).y == 2`; `Box(7).w == 7` with
`Box(7).h == 5` (trailing default). Twin: 0870 / 0871 (# pycsl-expected: FAIL)
assert the OLD false `== 0` claim (positional / keyword), which must NOT be provable.
"""
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Box:
    w: int
    h: int = 5


#@ ensures \result == 1
def positional_x() -> int:
    """The synthesized dataclass ctor binds field x from the first positional arg."""
    p = Point(1, 2)
    return p.x


#@ ensures \result == 2
def positional_y() -> int:
    """...and field y from the second (declaration order)."""
    p = Point(1, 2)
    return p.y


#@ ensures \result == 1
def keyword_x() -> int:
    """A keyword construction binds the same-named field."""
    p = Point(x=1, y=2)
    return p.x


#@ ensures \result == 2
def mixed_y() -> int:
    """A mixed positional+keyword construction binds each field once."""
    p = Point(1, y=2)
    return p.y


#@ ensures \result == 7
def partial_bound_w() -> int:
    """A partial call binds the provided positional prefix."""
    b = Box(7)
    return b.w


#@ ensures \result == 5
def partial_default_h() -> int:
    """...and a trailing OMITTED field keeps its declared default."""
    b = Box(7)
    return b.h


if __name__ == "__main__":
    assert positional_x() == 1
    assert positional_y() == 2
    assert keyword_x() == 1
    assert mixed_y() == 2
    assert partial_bound_w() == 7
    assert partial_default_h() == 5
    print("PASS")
