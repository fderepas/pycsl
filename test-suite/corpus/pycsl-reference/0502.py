"""Test 0502 — collections: namedtuple as a record (reuses Tier-A construction).

A module-level `Point = namedtuple('Point', ['x', 'y'])` synthesises a record type with an
implicit `__init__(self, x, y)` that sets the fields, so `Point(a, b)` builds `{x = a; y = b}`
via the Tier-A parametrized record construction and `p.x` is a record-field read. The field args
substitute through, so `p.x == a`. Only compile-time-literal fields (a list/tuple of str or a
`"x y"` string) are recognised; a dynamic fields arg keeps the factory opaque."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])


#@ requires a >= 0
#@ ensures \result == a
def first(a: int, b: int) -> int:
    p = Point(a, b)
    return p.x
