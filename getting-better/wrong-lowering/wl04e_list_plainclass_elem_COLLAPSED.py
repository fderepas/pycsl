"""WL-04e — `List[<plain-class-with-__init__>]` PARAM element field read — **FIXED**.

Before the fix: a flat `List[Point]` parameter, where `Point` is a PLAIN class with an
explicit positional `__init__` (`def __init__(self, x, y): self.x = x; self.y = y`) —
NOT a `@dataclass`/`NamedTuple`/recognized `Tuple` — was NOT recognized as a
list-element record, so the parameter collapsed to `array int` and `a[i].x` read the
opaque `get_x(a[i])` over an int element. A concrete construct-store-read-back field
property (`a[0] = Point(5, 6); return a[0].x  # == 5`) was UNPROVABLE (the opaque
`get_x` over the int-coerced ctor could not denote the written field). Verdict:
UNPROVEN (this store-read-back law); the plain read law proved only vacuously through
the opaque getter's syntactic identity.

After the fix (wrong-lowering-to-fix.md §WL-04 record residual, WL-04e): a plain
positional-`__init__` class is recognized as a content-faithful data record
(`_m5_is_plain_positional_record_class`), so `List[Point]` is realized as
`array point` — the record `point` emitted PURE (Why3 forbids a mutable element inside
`array`) — exactly like the WL-04b `@dataclass` path. `a[i]` reads a real `point`,
`a[i].x` projects the faithful field, and a constructed record stored into the array
(`a[0] = Point(5, 6)`, the faithful `{ x = 5; y = 6 }`) reads its written field back.
The true field property PROVES. Verdict: PROVEN."""
_ = 0
from typing import List


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


#@ requires len(a) > 0
#@ ensures \result == 5
def store_read(a: List[Point]) -> int:
    a[0] = Point(5, 6)
    return a[0].x


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].x
def read_field(a: List[Point], i: int) -> int:
    return a[i].x
