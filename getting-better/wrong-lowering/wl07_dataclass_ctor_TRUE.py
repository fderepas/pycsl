"""WL-07 — faithful `@dataclass` constructor field binding — POSITIVE driver.

The synthesized `@dataclass` constructor `Point(1, 2)` binds field `x` from the
first positional arg and `y` from the second (field-declaration order), plus the
keyword form `Point(x=1, y=2)`, the mixed form `Point(1, y=2)`, and a partial
call with a trailing default (`Box(7)` with `h: int = 5`). Every faithful field
law PROVES. Verdict: PROVEN (was UNPROVEN under the arg-drop bug).

(The two records use DISJOINT field names — `Point`{x,y} / `Box`{w,h} — to keep
each field label unqualified; a shared field name across two records forces
qualified Why3 labels, whose UNRELATED read-side de-qualification gap is a
separate pre-existing issue, orthogonal to the WL-07 constructor fix.)"""
_ = 0
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
    p = Point(1, 2)
    return p.x


#@ ensures \result == 2
def positional_y() -> int:
    p = Point(1, 2)
    return p.y


#@ ensures \result == 1
def keyword_x() -> int:
    p = Point(x=1, y=2)
    return p.x


#@ ensures \result == 2
def mixed_y() -> int:
    p = Point(1, y=2)
    return p.y


#@ ensures \result == 7
def partial_bound_w() -> int:
    b = Box(7)
    return b.w


#@ ensures \result == 5
def partial_default_h() -> int:
    b = Box(7)
    return b.h
