r"""Test 2260 — gen #36 ch16 (expected PASS): W-IPM S-A' — `self.<f>.sort()` and
`self.<f>.sort(key=lambda t: t.line)` on a `List[...]` field of a `@dataclass` are an
IN-PLACE havoc of the field's array: `array_sort_inplace self.xs` with `writes { a }`.

What proves, and why it is faithful: the length is unchanged (a Why3 array's length is
immutable; CPython's `list.sort` keeps the length), the other fields are unchanged (the
declared `#@ assigns self.xs` frame), and the sorted field IS in the effect, so an
`assigns \nothing` twin (2262) fails. Before ch16 both calls were REFUSED ("MUTATES its
receiver in place, and no certified lowering models it").
Twins: 2261 (positional content claim, must FAIL), 2262 (frame lie), 2263 (stale alias,
refused), 2264 (no_exception, refused), 2265 (effectful key, refused), 2267 (caller).
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class Tgt:
    line: int


@dataclass
class Tracker:
    xs: List[int] = field(default_factory=list)
    ts: List[Tgt] = field(default_factory=list)
    n: int = 0

    #@ ensures \length(self.xs) == \old(\length(self.xs))
    #@ ensures self.n == \old(self.n)
    #@ assigns self.xs
    def order(self) -> None:
        self.xs.sort()

    #@ ensures \length(self.ts) == \old(\length(self.ts))
    #@ assigns self.ts
    def order_by_line(self) -> None:
        self.ts.sort(key=lambda t: t.line)


if __name__ == "__main__":
    t = Tracker([3, 1, 2], [Tgt(5), Tgt(2)], 4)
    t.order()
    t.order_by_line()
    assert t.xs == [1, 2, 3] and len(t.ts) == 2 and t.ts[0].line == 2 and t.n == 4
