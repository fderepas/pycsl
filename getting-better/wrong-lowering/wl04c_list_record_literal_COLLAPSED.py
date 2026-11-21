"""WL-04c — `List[<record>]` LITERAL element field read — **FIXED**.

Before the fix: a list LITERAL of record constructors (`a = [Point(1, 2),
Point(3, 4)]`, `return [Point(1, 2), Point(3, 4)]`) ran every element through
`_coerce_to_int`, so the local's `a[i].field` was projected through the opaque
`get_field` over a collapsed int (content-opaque and, at a record use site,
ill-typed → TYPEERR). Verdict: TYPEERR.

After the fix (wrong-lowering-to-fix.md §WL-04 record literal residual): a list
literal whose elements are ALL full-arity constructor calls to the SAME
content-faithful record (a NamedTuple / recognized `Tuple` / explicit-`__init__`
positional class) builds `array <record>` with each element the FAITHFUL record
literal (`{ x = 1; y = 2 }` via the record constructor), so `a[i].field` on the
local (registered as a record-array local) projects the real field. The record is
emitted PURE (Why3 forbids a mutable element inside `array`). The true field law
PROVES. Verdict: PROVEN."""
_ = 0
from typing import NamedTuple, List


class Point(NamedTuple):
    x: int
    y: int


#@ ensures \result == 1
def first_x() -> int:
    """A record-list LITERAL local's element field is a native record projection."""
    a = [Point(1, 2), Point(3, 4)]
    return a[0].x


#@ ensures \result == 4
def second_y() -> int:
    a = [Point(1, 2), Point(3, 4)]
    return a[1].y
