"""WL-05d (T8) — a RECORD/@dataclass PARAMETER field store `p.x = v` is FAITHFUL and
caller-visible (verdict PROVEN).

A standalone (non-list-element) @dataclass param is a MUTABLE Why3 record
`{ mutable x; mutable y }`; `p.x = v` lowers to the NATIVE `p.x <- v`, and Why3 INFERS
the `writes {p.x}` frame on the concrete `let` — so the write-read-back `ensures p.x == 5`
PROVES. Previously the store was silently DROPPED (Module 5 emitted no IR) → a no-op."""
_ = 0
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ ensures p.x == 5
def setx(p: Point) -> None:
    p.x = 5
