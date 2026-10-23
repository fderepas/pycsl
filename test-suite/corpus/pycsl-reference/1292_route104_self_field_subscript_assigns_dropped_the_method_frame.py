# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1292 — (#49) ROUTE #104 EXPLOIT ARM: `#@ assigns self.xs[0]` on a `\\trusted` METHOD
contributed NO field to the method-writes map, so the method's `val` got no frame at all.

The two frame collectors in `_emit_frame_condition` deliberately SKIP every `self.<field>`
and defer to `_build_method_writes_map` (functions.py) — a method's self-writes become the
val's `writes` there, and re-emitting one in the collector produced an unbound/duplicate
target. That deferral is correct. The map it defers to was keyed on the NODE TYPE:

    a.get("type") in ("FieldGet", "Attribute") and a.get("object") == "self"

and `#@ assigns self.xs[0]` lowers to `Subscript(FieldGet(self, "xs"), 0)` — neither. So the
target fell out of the map and the `val` was emitted with no `writes`.

>>> A DEFERRAL IS AN UNVERIFIED CROSS-REFERENCE THAT READS EXACTLY LIKE A GUARD. The comment
>>> deferring to the map is TRUE for the spelling its author had in view and FALSE for this
>>> one; locating the named guard and reading ITS ACTUAL MATCHING RULE is what found this.

MEASURED AT 5795cfef, and the POSITIVE CONTROL FIRED, which is what makes this a finding
rather than a story:

    #@ assigns self.xs      ->  `writes` emitted  ->  `ensures \\result == 7` FAILS (honest)
    #@ assigns self.xs[0]   ->  no `writes`       ->  the same `ensures` PROVES

while CPython returns 5. And there is NO range escape hatch for a self-field:
`#@ assigns self.xs[0..1]` is a PARSE ERROR (`_parse_assigns_region` calls `expect_name()`,
which cannot accept a dotted base), so the single-index spelling is the ONLY way to say "this
method writes into self.xs[i]" — and it was the unsound one.

Must FAIL.
"""


class Box:
    def __init__(self) -> None:
        self.xs = [7, 7, 7]

    #@ \trusted reviewer: route104
    #@ requires \length(self.xs) > 0
    #@ assigns self.xs[0]
    def poke(self) -> None:
        self.xs[0] = 5

    #@ requires \length(self.xs) > 0
    #@ requires self.xs[0] == 7
    #@ ensures \result == 7
    def driver(self) -> int:
        self.poke()
        return self.xs[0]
